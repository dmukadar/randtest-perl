#!/usr/bin/perl -w
use strict;

use DBI;
use JSON::PP;
use File::Copy;
use Time::Piece;
use FindBin qw($Bin);
# use Data::Dumper;

sub convert {
    my $stringTime = shift(@_);

    #asumsi: format stringTime TUE SEP 01 18:16:32:150 2015
    if (defined $stringTime && $stringTime ne "") {
        $stringTime =~ s/:\d{2,3} / /;

        my $time = Time::Piece->strptime($stringTime, "%a %b %d %T %Y");

        return $time->strftime('%Y-%m-%d %T');
    }

    return '0000-00-00 00:00:00';
}

my %stat;
my %calls;
my %record;
my $charCount = 0;
my $lineCount = 0;
my $recordCount = 0;
my $uploadDir = "$Bin/uploads";
my $filesize = -s "$uploadDir/spool.txt";
my %config = (
    "dsn"      => "DBI:mysql:database=perltestdb;host=127.0.0.1;port=3306",
    "uname"    => "tester1",
    "password" => "1"
);
my $queries =<<'EOL';
INSERT INTO cdr (acctSessionId, callingStationId, calledStationId, setupTime, connectTime, disconnectTime) 
VALUES (?, ?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE callingStationId = ?, calledStationId = ?, setupTime = ?, connectTime = ?, disconnectTime = ?
EOL

if (-f "$uploadDir/spool.txt") {
    my $dblink = DBI->connect(
        $config{"dsn"},
        $config{"uname"},
        $config{"password"},
        { RaiseError=>1, AutoCommit=>0 }
    );
    my $setupTime;
    my $connectTime;
    my $disconnectTime;
    my $statement = $dblink->prepare($queries);

    open(my $handler, "<", "$uploadDir/spool.txt");
    LINE: while (my $row = <$handler>) {
        $lineCount++;
        $charCount += length($row);
        if ($row =~ /^(sun|mon|tue|wed|thu|fri|sat) .*20\d{2}$/i) {
            # print "NEW RECORD FOUND\r\n";
            %record = ();
            $recordCount++;
            next LINE;
        }
        if ($row =~ /^$/) {
            #save to db;
            # print "SAVING RECORD TO DB\r\n";
            # print Dumper(\%record);
            $calls{$record{"Acct-Session-Id"}}++;

            $setupTime = convert($record{"setup-time"});
            $connectTime = '0000-00-00 00:00:00';
            $disconnectTime = convert($record{"disconnect-time"});

            # last;
            $statement->execute(
                $record{"Acct-Session-Id"}, $record{"Calling-Station-Id"}, $record{"Called-Station-Id"}, $setupTime, $connectTime, $disconnectTime,
                $record{"Calling-Station-Id"}, $record{"Called-Station-Id"}, $setupTime, $connectTime, $disconnectTime,
            );

            next LINE;
        }
        chomp($row);
        # print $row, "\r\n";
        if ($row =~ /^\s(\w.*?) = "?(.*?)"?$/) {
            $record{$1} = $2;
        }
    }
    close($handler);
    if ($dblink->commit()) {
        my $time = localtime;
        my $filecopy = $time->strftime("$uploadDir/processed-%Y%m%d_%H%M%S.txt");
        copy("$uploadDir/spool.txt", $filecopy);

        unlink("$uploadDir/spool.txt") if (-e $filecopy);
    }
    $dblink->disconnect();
}

%stat = (
    'filesize'   => $filesize,
    'current'    => $charCount,
    'line-read'  => $lineCount,
    'record-read'=> $recordCount,
    'call-read'  => (scalar keys %calls)
);

print "Content-Type: application/json\r\n\r\n";
print encode_json \%stat;