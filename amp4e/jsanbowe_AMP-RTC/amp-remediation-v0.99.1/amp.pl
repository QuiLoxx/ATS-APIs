#!/usr/bin/perl
###############################################################################
#
# Copyright (C) 2017 Cisco and/or its affiliates. All rights reserved.
#
# THE PRODUCT AND DOCUMENTATION ARE PROVIDED AS IS WITHOUT WARRANTY
# OF ANY KIND, AND CISCO DISCLAIMS ALL WARRANTIES AND REPRESENTATIONS,
# EXPRESS OR IMPLIED, WITH RESPECT TO THE PRODUCT, DOCUMENTATION AND
# RELATED MATERIALS INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE; WARRANTIES
# ARISING FROM A COURSE OF DEALING, USAGE OR TRADE PRACTICE; AND WARRANTIES
# CONCERNING THE NON-INFRINGEMENT OF THIRD PARTY RIGHTS.
#
# IN NO EVENT SHALL CISCO BE LIABLE FOR ANY DAMAGES RESULTING FROM
# LOSS OF DATA, LOST PROFITS, LOSS OF USE OF EQUIPMENT OR LOST CONTRACTS
# OR FOR ANY SPECIAL, INDIRECT, INCIDENTAL, PUNITIVE, EXEMPLARY OR
# CONSEQUENTIAL DAMAGES IN ANY WAY ARISING OUT OF OR IN CONNECTION WITH
# THE USE OR PERFORMANCE OF THE PRODUCT OR DOCUMENTATION OR RELATING TO
# THIS AGREEMENT, HOWEVER CAUSED, EVEN IF IT HAS BEEN MADE AWARE OF THE
# POSSIBILITY OF SUCH DAMAGES.  CISCO'S ENTIRE LIABILITY TO LICENSEE,
# REGARDLESS OF THE FORM OF ANY CLAIM OR ACTION OR THEORY OF LIABILITY
# (INCLUDING CONTRACT, TORT, OR WARRANTY), SHALL BE LIMITED TO THE
# LICENSE FEES PAID BY LICENSEE TO USE THE PRODUCT.
#
###############################################################################
#
#  Change Log
#
#  03-Jan-2018 - Jamie Sanbower
#    Initial release
#
###############################################################################
#
# AMP Remediation Module
#
# Jamie Sanbower - 1/3/2018  - Version 0.99
#
# This remediation uses theAMP API to change the endpoint group to apply
# different policies based on remediation configuration.
#
###############################################################################
use strict;
use warnings;

use FindBin;
use SF::Logger;
use XML::Simple;
use IO::Socket::SSL qw( SSL_VERIFY_NONE );

use lib "$FindBin::Bin/_lib_";
use Constants;
use LWP::UserAgent;
use Net::Netmask;


###############################################################################
# Main
###############################################################################

# Load Config File
# FOR TESTING USE THE INSTANCE name my $config_file = './JAMIE/instance.conf';
my $config_file = "instance.conf";

# Get and save the program name, without path
my $prog = $0;
$prog =~ s/^.*\///;

# Show usage if not enough parameters
if (@ARGV < 5)
{
    warn("Usage: $prog <remediation_type> <ip> <policy> <rule_id> <sid>\n\n");
    exit(INPUT_ERR);
}

# Get the parameters
my ($rem,              # Remediation type
    $ip,               # Address to be killed
    $policy,           # Compliance Policy that called this remediation
    $rule,             # Compliance Rule that called this remediation
    $sid) = @ARGV;     # SID that fired (if this was an intrusion event based rule)

# create xml object
my $xml = new XML::Simple;

# read XML file
my $data = $xml->XMLin($config_file, ForceArray=>['network_li', 'string']);

# Move Data into variables
my $apiclient  = $data->{config}->{string}->{user_name}->{content};
my $apikey  = $data->{config}->{password}->{content};
my $groupname = $data->{config}->{string}->{group_name}->{content};
my $log   = $data->{config}->{boolean}->{content};

# DEBUG ONLY (set to 1)
my $debug = 0;
print "API Client: $apiclient\nAPI Key: $apikey\nGroup Name: $groupname\nIP: $ip\n" if $debug;

# Enable or disable logging
$log eq 'true' ? SF::Logger::enableLogging() : SF::Logger::disableLogging();

logInfo('Starting AMP remediation');

# Whitelist Check
if ($data->{config}->{list}->{network_li}) {
    foreach my $list (@{$data->{config}->{list}->{network_li}}) {
	my $netblock = Net::Netmask->new($list);
        if ($netblock->match($ip)) {
            logInfo("Whitelist match ($ip is in $netblock): Remediation aborted");
            print "Whitelist match ($ip is in $netblock): Remediation aborted\n" if $debug;
	    exit(WHITELIST);
        }
    }
}


# Call our subs that makes the requests.
my $compid = get_compID();
my $groupid = get_groupID();
my $returnstatus = set_group($compid,$groupid);


logInfo("AMP Remediation Success: $returnstatus"); 
exit;

# if we get here something unhandled happened...
logWarn("We encountered an unhandled exception: $returnstatus");

exit(UNDEF);


###############################################################################
# Functions
###############################################################################

# Get Computer  UID
sub get_compID
{
	
	
	my $results = `curl -s -k -X GET -H 'accept: application/json' -H 'content-type: application/json' --compressed -H 'Accept-Encoding: gzip, deflate' -u $apiclient:$apikey 'https://api.amp.cisco.com/v1/computers?internal_ip=$ip'`;
        if ($results =~ /"total":0/) {
		warn("The Computer was NOT found in the AMP Cloud");
		logInfo('The Computer was NOT found in the AMP Cloud');
    		exit(INPUT_ERR);
	} elsif ($results =~ /error_code":401/) {
		warn("Unuauthorized AMP API Credentials");
                logInfo('Unuauthorized AMP API Credentials');
                exit(2);

	} else {
		$results =~ s/.*connector_guid":"([^"]*).*/$1/gi;
        	print "Computer ID: :$results\n" if $debug;
        	return $results;
	}
}

# Get Group UID
sub get_groupID
{

        my $results = `curl -s -k -X GET -H 'accept: application/json' -H 'content-type: application/json' --compressed -H 'Accept-Encoding: gzip, deflate' -u $apiclient:$apikey 'https://api.amp.cisco.com/v1/groups?name=$groupname'`;
        if ($results =~ /guid":"([^"]*).*/) {
                print "Group ID: $1\n" if $debug;
                return $1;
        } else {
                warn("The Group was NOT found in the AMP Cloud");
                logInfo('The Group was NOT found in the AMP Cloud');
                exit(2);
        }
}

# Set Computers Group
sub set_group
{
	
	my ($comp, $group) = (@_);
	my $results = `curl -s -k -X PATCH -H 'accept: application/json' -H 'content-type: application/json' -H 'content-length: 53' --compressed -H 'Accept-Encoding: gzip, deflate' -d '{"group_guid":"$group"}' -u $apiclient:$apikey 'https://api.amp.cisco.com/v1/computers/$comp'`;
	print "My Results: $results\n" if $debug;
	return("Put IP:$ip($comp) intto $groupname($group)");
}

# Info logging
sub logInfo
{
    my ($msg) = @_;

    # Update the message with our standard bits
    if ($sid) {
        $msg = "[$$] quar_ip:$ip ($policy->$rule sid:$sid) $msg";
    } else {
        $msg = "[$$] quar_ip:$ip ($policy->$rule) $msg";
    }

    SF::Logger::sfinfo($prog, $rem, $msg);
}

# Warning logging
sub logWarn
{
    my ($msg) = @_;

    # Update the message with our standard bits
    if ($sid) {
        $msg = "[$$] quar_ip:$ip ($policy->$rule sid:$sid) $msg";
    } else {
        $msg = "[$$] quar_ip:$ip ($policy->$rule) $msg";
    }

    SF::Logger::sfwarn($prog, $rem, $msg);
}