#!/usr/bin/perl -w
use strict;
use HTML::Template;
use FindBin qw($Bin);
use CGI qw(:standart);

my @errorMessage;
my $cgi = CGI->new;
my $uploadDir = "$Bin/uploads";
my $template = HTML::Template->new(filename => 'tmpl/progress.html');

push (@errorMessage, 'Cannot find log file, please upload log using previous page') unless -f "$uploadDir/spool.txt";

my $baseUrl = $cgi->url();
$baseUrl =~ s/\/\w*?\.cgi$//;
$template->param(
    'base_url'=>$baseUrl,
    'asset_url'=>'/radtest-assets/'
);

if (@errorMessage) {
    $template->param(
        'error_message'=>join('<br/>', @errorMessage)
    );
}

print $cgi->header, $template->output;