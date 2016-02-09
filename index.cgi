#!/usr/bin/perl -w
use strict;
use File::Copy;
use HTML::Template;
use FindBin qw($Bin);
use CGI qw(:standart);


my @errorMessage;
my $cgi = CGI->new;
my $uploadDir = "$Bin/uploads";
my $template = HTML::Template->new(filename => 'tmpl/index.html');

unless (-d $uploadDir) {
    mkdir($uploadDir, 0700) || push @errorMessage, 'Cannot create upload directory';
}
if ($cgi->param) {
    my $logfile = $cgi->upload('logfile');
    if (! defined $logfile) {
        push @errorMessage, 'Can not find file';
    } else {
        my $filename = $cgi->param('logfile');
        my $type = $cgi->uploadInfo($filename)->{'Content-Type'};

        if ($type ne 'text/plain') {
            push @errorMessage, 'Log should be a text file';
        } else {
            $filename = $cgi->tmpFileName($logfile);

            if (! copy($filename, $uploadDir . '/spool.txt')) {
                push @errorMessage, 'Cannot copy log file';
            } else {
                unlink($filename);
                print $cgi->redirect('process.cgi');        
                exit;
            }
        }


    }

}

my $baseUrl = $cgi->url();
$baseUrl =~ s/\/\w*?\.cgi$//;
$template->param(
    'base_url'=>$baseUrl,
    'asset_url'=>'/radtest-assets/',
);

if (@errorMessage) {
    $template->param(
        'error_message'=>join('<br/>', @errorMessage)
    );
}

print $cgi->header, $template->output;