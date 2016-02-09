#!/usr/bin/perl -w
use strict;
use DBI;
use POSIX;
use HTML::Template;
use CGI qw(:standart);
use Data::Dumper;

my @errorMessage;
my $cgi = CGI->new;
my $template = HTML::Template->new(filename => 'tmpl/result.html');
my %config = do 'config.pl';
my $page = 1;
my $rowLimit = 10;
my $totalPage;
my $offset;
my $dblink = DBI->connect(
    $config{"dsn"},
    $config{"uname"},
    $config{"password"},
    { RaiseError=>0, AutoCommit=>1 }
);
my $searchCondition;
my $keyword = $cgi->param('query');
my $list;
my $queries;
my @row;

if (defined $keyword) {
    @row = $dblink->selectrow_array("SELECT COUNT(-1) FROM cdr WHERE acctSessionId LIKE ?", {}, "%$keyword%");
} else {
    @row = $dblink->selectrow_array("SELECT COUNT(-1) FROM cdr");
}

my $rowCount = shift(@row);    
$page = $cgi->param('page');
$totalPage = ceil($rowCount / $rowLimit);

if (! defined $page) {
    $page = 1;
} else {
    $page = $totalPage unless $page < $totalPage;
}

$offset = ($page - 1) * $rowLimit;

if (defined $keyword) {
    $queries = <<"EOL";
    SELECT 
        acctSessionId, callingStationId, calledStationId, setupTime, connectTime, disconnectTime
    FROM cdr
    WHERE acctSessionId LIKE ?
    LIMIT $offset, $rowLimit
EOL

    $list = $dblink->selectall_arrayref($queries, { Slice=>{} }, "%$keyword%");
} else {
    $queries = <<"EOL";
    SELECT 
        acctSessionId, callingStationId, calledStationId, setupTime, connectTime, disconnectTime
    FROM cdr
    LIMIT $offset, $rowLimit
EOL

    $list = $dblink->selectall_arrayref($queries, { Slice=>{} });
}


my $baseUrl = $cgi->url();
$baseUrl =~ s/\/\w*?\.cgi$//;
$template->param(
    'base_url'      =>$baseUrl,
    'asset_url'     =>'/radtest-assets/',
    'search_results'=> $list,
    'total_page'    => $totalPage,
    'search_query'  => $keyword,
);

if (@errorMessage) {
    $template->param(
        'error_message'=>join('<br/>', @errorMessage)
    );
}

print $cgi->header, $template->output;