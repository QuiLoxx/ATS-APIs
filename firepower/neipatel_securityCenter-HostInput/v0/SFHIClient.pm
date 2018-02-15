package SFHIClient;

use strict;
use warnings;

BEGIN
{
    use SFCheckPreReq;
    SFCheckPreReq::assertModules(['Socket',
                                  'IO::Socket::SSL']);
}

use Socket;
use IO::Socket::SSL;

# determine if IPv6 is present
our $IPV6_THERE;
eval{
    require Socket6;
    require IO::Socket::INET6;
};
$IPV6_THERE = 1 unless $@;

# control debug output
our $debug = 0;


# common code between client and server
our ($HI_TYPE_MAX_SIZE,$HI_TYPE_VERSION,$HI_TYPE_DATA,$HI_TYPE_ERROR) = (1,2,3,4);


# Create a new SSL client socket
sub newClient
{
    my ($server,$port,$crtfile,$keyfile,$proto) = @_;
    # Create the ssl connection to the host input server
    if( ! -e $crtfile )
    {
        die "Certificate file $crtfile doesn not exist";
    }
    if( ! -e $keyfile )
    {
        die "Key file $keyfile doesn not exist";
    }
    my $domain=AF_INET;
    if($proto eq "AF_INET")
    {
        $domain=AF_INET;
    }
    elsif ($proto eq "AF_INET6")
    {
        $domain=AF_INET6;
    }

    my $client = IO::Socket::SSL->new(
                                       Domain => $domain,
                                       PeerAddr => "$server",
                                       PeerPort => "$port",
                                       Proto => 'tcp',
                                       SSL_use_cert => 1,
                                       SSL_cert_file => "$crtfile",
                                       SSL_key_file => "$keyfile",
                                       SSL_verify_mode => 0   );
    return $client;
}

# Remove ',' '^M' non-necessary characters from a string
sub reformat
{
    my ($str) = @_;

    # need to remove ',' '\"'
    $str =~ s/,/ /g;
    $str =~ s/\"/'/g;
    $str =~ s/\n/ /g;
    $str =~ s/\cM/ /g;
    return $str;
}

# Format CVE ID string or BugTraq ID string in CSV format
sub formatStrIDCmd
{
    my ($head,$id_array,$sub_head) = @_;

    my @str_list;
    $sub_head = "" if( !defined($sub_head) );
    foreach my $item (@{$id_array})
    {
        push @str_list,$sub_head.$item;
    }

    return $head.join ' ',@str_list;
}

# Add one CSV command line format to an existing CSV string
sub addCSVCommand
{
    my ($cmd) = @_;

    my $csv_string;

    $csv_string = "\n" if($cmd eq 'ScanFlush');
    $csv_string .= $cmd."\n";

    return $csv_string;
}

# Send data to server based on TLV (type, length, value) format
sub SendToServer
{
    my ($sock,$type,$size,$data) = @_;

    my ($len,$rlen);

    # send type & size
    my $ts = pack('NN', $type,$size);
    $rlen = syswrite($sock, $ts, length($ts));
    if( $! || !defined($rlen) )
    {
        die "syswrite error: $!";
    }

    # send data
    if( $type == $HI_TYPE_VERSION )
    {
        my $v = pack('N', $data);
        $rlen = syswrite($sock, $v, length($v));
        if( $! || !defined($rlen) )
        {
            die "syswrite error: $!";
        }
    }
    else
    {
        $len = 0;
        while( $len < $size )
        {
            $rlen = syswrite($sock, $data, $size, $len);
            last if(!$rlen);
            if( $! || !defined($rlen) )
            {
                die "syswrite error: $!";
            }
            $len += $rlen;
        }
    }
}

# receive data from server and return the data received
# if error happened in sysread(), exit from client application
sub ReceiveFromServer
{
    my ($sock) = @_;

    my ($t,$type,$s,$size,$rlen,$len,$text);

    $t = getBinaryData($sock,4);
    $type = unpack('N',$t);

    $s = getBinaryData($sock,4);
    $size = unpack('N',$s);

    warn "ReceiveFromServer(): Type: $type, Size: $size" if $debug;

    if( $type == $HI_TYPE_MAX_SIZE )
    {
        $text = getBinaryData($sock,$size);
        $text = unpack('N',$text);
    }
    else
    {
        $text = getBinaryData($sock,$size);
        warn "Server Message: ".$text if $debug;
    }
    return $text;
}

# generic function to read data from socket
sub getBinaryData
{
    my ($sock,$size) = @_;

    my ($rlen,$len,$bytes_data);

    # read in bytes in $len
    $len = 0;
    while( $len < $size )
    {
        $rlen = sysread($sock,$bytes_data,$size,$len);
        if( $! || !defined($rlen) || $rlen < 0 )
        {
            die "sysread error: $!";
        }
        elsif($rlen == 0)
        {
            warn "exiting";
            if ($sock)
            {
                $sock->close();
                exit 0;
            }
        }
        $len += $rlen;
    }
    return undef if( $rlen == 0 );
    return $bytes_data;
}

sub mem_report
{
    my $rval = '';
    my @lines = `top -bn 1 -p $$`;
    foreach my $line (@lines)
    {
        $rval .= '    '. $line if ($line =~ /PID/);
        $rval .= '    '. $line if ($line =~ /$$/);
    }
    return $rval;
}

1;
