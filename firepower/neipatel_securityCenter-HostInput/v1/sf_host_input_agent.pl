#!/usr/bin/perl

use strict;
use warnings;
#added to make sure bin in working directory are used
use FindBin;
use lib $FindBin::Bin;
BEGIN
{
    use SFCheckPreReq;
    SFCheckPreReq::assertModules(['SFHostInputAgent',
                                  'Getopt::Long']);
}


use SFHostInputAgent;
use Getopt::Long;

sub main
{
    my $opts;
    my $ret = GetOptions ( "port=i"       => \$opts->{port},
                           "pkcs12=s"     => \$opts->{pkcs12},
                           "password=s"   => \$opts->{password},
                           "plugininfo=s" => \$opts->{plugininfo},
                           "server=s"     => \$opts->{server},
                           "runondc=s"    => \$opts->{runondc},
                           "csvfile=s"    => \$opts->{csvfile},
                           "syslog"       => \$opts->{syslog},
                           "stderr"       => \$opts->{stderr},
                           "logfile=s"    => \$opts->{logfile},
                           "level=i"      => \$opts->{level},
                           "ipv6"         => \$opts->{ipv6_flag},
                         );
    die "Specifying Unknown Options" unless $ret;

    my $agent = SFHostInputAgent->new($opts);
    $agent->process();
}

eval
{
    main();
};

if( $@ )
{
    warn "Error detected during run of Host Input Agent: ".$@;
    exit(2);
}
