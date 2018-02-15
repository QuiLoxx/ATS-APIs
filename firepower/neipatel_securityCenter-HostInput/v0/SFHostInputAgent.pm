package SFHostInputAgent;

use strict;
use warnings;

BEGIN
{
    use SFCheckPreReq;
    SFCheckPreReq::assertModules(['SFPkcs12',
                                  'SFHIClient',
                                  'SFHILog']);
}

use SFPkcs12;
use SFHIClient;
use SFHILog;

my $VERSION = '1.0.1-8';
my $DEFAULT_PORT = 8307;

#
# Setup Signal Handlers
#
$SIG{TERM} = \&signalHandler;
$SIG{INT}  = \&signalHandler;



sub new
{
    my $class = shift;
    my ($opts) = @_;

    my $self;

    # Get input methods
    $self = registerPlugins($self);

    bless $self, $class;

    # Parse the command line args
    $self->processCommandLine($opts);

    return $self;
}

my $sendData_max_size = 4000;
my $sendData_buf = '';
my $sendData_buf_len = 0;
sub sendData
{
    my $self = shift;

    my ($buf) = @_;

    return if(!$buf);

    my $buf_len = length($buf);

    # If the buffer is full or we are explicitly flushing
    if ($sendData_buf_len + $buf_len > $sendData_max_size)
    {

        $self->{LOG}->log($SFHILog::DEBUG,"Sent command(s) of length ". $sendData_buf_len);
        SFHIClient::SendToServer($self->{CLIENT}, $SFHIClient::HI_TYPE_DATA, $sendData_buf_len, $sendData_buf);
        my $text = SFHIClient::ReceiveFromServer($self->{CLIENT});
        $self->{LOG}->log($SFHILog::DEBUG,"Defense Center (".$self->{OPTIONS}{server}.") Response:\n$text") if($text);

        $sendData_buf = $buf;
        $sendData_buf_len = $buf_len;
    }

    # Otherwise buffer it up
    else
    {
        $sendData_buf .= $buf;
        $sendData_buf_len += $buf_len;
    }
}

sub flushSendBuffer
{
    my $self = shift;

    if ($sendData_buf_len > 0)
    {
        $self->{LOG}->log($SFHILog::DEBUG,"Sent command(s) of length ". $sendData_buf_len);
        SFHIClient::SendToServer($self->{CLIENT}, $SFHIClient::HI_TYPE_DATA, $sendData_buf_len, $sendData_buf);
        my $text = SFHIClient::ReceiveFromServer($self->{CLIENT});
        $self->{LOG}->log($SFHILog::DEBUG,"Defense Center (".$self->{OPTIONS}{server}.") Response:\n$text") if($text);
    }
    $sendData_buf = '';
    $sendData_buf_len = 0;
}

sub signalHandler
{
    my $self = shift;

    my ($sig) = @_;
    if($self->{CLIENT})
    {
        close $self->{CLIENT};
        $self->{LOG}->log($SFHILog::INFO,"Client closed on Socket.");
    }
    $self->{LOG}->log($SFHILog::INFO,"-Caught Signal ($sig)");
    exit(1);
}

sub getLogger
{
    my $self = shift;

    return $self->{LOG};
}

sub getOptions
{
    my $self = shift;

    return $self->{OPTIONS};
}

#
# If we get here...stuff is wrong...print usage and exit non-zero.
#
sub usage
{
    my $self = shift;

    my $prog = $0;
    if ($0 =~ /\/([^\/]+)$/)
    {
        $prog = $1;
    }
    warn "\n$prog Ver. $VERSION\n";
    warn "\nusage: $prog [options] <plugin>\n";
    warn "Options:\n";
    warn "\t[-se]rver=<server address>\n";
    warn "\t[-po]rt=<server port>               (default: $DEFAULT_PORT)\n";
    warn "\t[-pk]cs12=<path to pkcs12 file>     (default: autodetect)\n";
    warn "\t[-pa]ssword=<pkcs12 password>       (default: none)\n";
    warn "\t[-pl]ugininfo=<any string passed into plugin module>\n";
    warn "\t[-sy]slog\n";
    warn "\t[-st]derr\n";
    warn "\t[-lo]gfile=<log file>\n";
    warn "\t[-le]vel=<log level> (3: debug, 2: info, 1: warning, 0: error)\n";
    warn "\t[-m]ultiinfo=<any string passed into running multiple instance>\n" if($prog =~ /process_multiple.pl/);
    #warn "\t[-r]unondc=<'y' or 'n'>\n";
    warn "\t[-c]svfile=<CSV output filename>\n";
    warn "\t[-i]pv6\t\tNote: Enabling this will switch communications to IPv6 only\n";
    warn "\n";
    warn "Supported Plugins:\n";
    for my $plugin (sort keys %{$self->{PLUGINS}}){
        warn "    $plugin:\t$self->{PLUGINS}{$plugin}{description}\n";
        warn "\t- Info:\t$self->{PLUGINS}{$plugin}{info}\n";
        warn "\t- Parameters:\n$self->{PLUGINS}{$plugin}{parameters}" if(defined($self->{PLUGINS}{$plugin}{parameters}));
        warn "\n";
    }

    warn "\n";
    exit (1);
}

#
# Register input plugins
#
sub registerPlugins
{
    my $self_obj = shift;

    my @plugins = glob("InputPlugins/*.pm");
    die "No input plugins found in InputPlugins directory\n" if !@plugins;

    for my $module (@plugins){
        my ($plugin) = ($module =~ m/InputPlugins\/(.*)\.pm$/);
        my $info = eval "require InputPlugins::$plugin; return InputPlugins::$plugin"."::register();";

        if($info){
            $self_obj->{PLUGINS}{$plugin} = $info;
        }else{
            warn "Error loading plugin '$plugin': $@\n";
        }
    }
    return $self_obj;
}

#
# Process the command line
#
sub processCommandLine
{
    my $self = shift;

    my ($opts) = @_;

    my $ipv6_flag;
    my $log_params;
    my $pkcs12_opts;
    my $INPUT_PLUGIN;
    my $HILogger;

    $opts->{runondc} = (lc($opts->{runondc}) eq 'y') ? 'y' : 'n';  # turn it off if not set
    $opts->{port} = $DEFAULT_PORT if(!$opts->{port} && $opts->{runondc} eq 'n');


    $log_params->{syslog} = $opts->{syslog};
    $log_params->{stderr} = $opts->{stderr};
    $log_params->{logfile} = $opts->{logfile};
    $log_params->{loglevel} = $opts->{level};
    $ipv6_flag = $opts->{ipv6_flag};

    # Toggle IPv6/IPv4 Connectivity
    if ($ipv6_flag)
    {
        die "Required IPv6 perl Module (IO::Socket::INET6) failed to load\n"
            unless $SFHIClient::IPV6_THERE;
        $opts->{proto} = "AF_INET6";
    }
    else
    {
        $opts->{proto} = "AF_INET";
    }

    #
    # Grab the server from the command line OR usage
    #
    if (!defined($opts->{plugin}))
    {
        $opts->{plugin} = shift @ARGV;
    }

    # Handle logging parameters
    $log_params->{plugin} = $opts->{plugin};
    $HILogger = SFHILog->new($log_params);
    $pkcs12_opts->{HILog} = $HILogger;
    $opts->{logging} = $HILogger;

    # If this is client and not outputing to CSV file
    if( $opts->{runondc} eq 'n' && !defined($opts->{server}) && !$opts->{csvfile} )
    {
        $HILogger->log($SFHILog::ERROR,"Client Does Not Specify Server IP to Connect to");
        $self->usage();
    }

    # Initialize plugin
    if( !defined $opts->{plugin} )
    {
        $HILogger->log($SFHILog::ERROR,"Please Specify Which Plugin Will Be Using");
        $self->usage();
    }
    $INPUT_PLUGIN = $self->{PLUGINS}{$opts->{plugin}};
    if( !defined $INPUT_PLUGIN )
    {
        $HILogger->log($SFHILog::ERROR,"Can Not Find the Plugin Specified: '$opts->{plugin}'");
        $self->usage();
    }
    my $rc = &{$INPUT_PLUGIN->{init}}($opts);
    if( $rc == -1 )
    {
        $HILogger->log($SFHILog::ERROR,"Plugin '$opts->{plugin}' Initialization Fails");
        $self->usage();
    }

    $self->{OPTIONS} = $opts;
    $self->{PKCS12_OPTS} = $pkcs12_opts;
    $self->{INPUT_PLUGIN} = $INPUT_PLUGIN;
    $self->{LOG} = $HILogger;
}

sub printOptions
{
    my $self = shift;

    my $str = "\n\nCommand Options:\n";
    while( my ($opt,$value) = each %{$self->{OPTIONS}} )
    {
        if (defined $value && ref($value) eq 'SFHILog')
        {
            $str .= "\t- $opt: SFHILog\n";
        }
        elsif ( $opt eq 'runondc')
        {
            next;
        }
        elsif ( defined $value && $value )
        {
            $str .= "\t- $opt: $value\n";
        }
    }
    $self->{LOG}->log($SFHILog::DEBUG,"$str\n");
}

sub process
{
    my $self = shift;

    # If we run it on DC, many options are NOT needed
    my $opts = $self->{OPTIONS};
    if( $opts->{runondc} eq 'y' || $opts->{csvfile} )
    {
        # 'server', 'port', 'pkcs12', 'password', 'ipv6'
        if( $opts->{server} || $opts->{port} || $opts->{pkcs12} ||
            $opts->{password} || $opts->{ipv6} )
        {
            my $log_str = $opts->{server} ? "-server $opts->{server} " : '';
            $log_str .= $opts->{port} ? "-port $opts->{port} " : '';
            $log_str .= $opts->{pkcs12} ? "-pkcs12 $opts->{pkcs12} " : '';
            $log_str .= $opts->{password} ? "-password $opts->{password} " : '';
            $log_str .= $opts->{ipv6} ? "-ipv6 $opts->{ipv6} " : '';
        }
    }
    $self->printOptions();

    my $str_ptr = &{$self->{INPUT_PLUGIN}{input}}();
    #$self->{LOG}->log($SFHILog::DEBUG,"Current Memory Utilization :\n". SFHIClient::mem_report());

    if(!$$str_ptr)
    {
        $self->{LOG}->log($SFHILog::INFO,"No data to process for plugin ".$self->{OPTIONS}{plugin});
        return;
    }

    # write to a file if needed
    if( $self->{OPTIONS}{csvfile} )
    {
        my $csv_file = $self->{OPTIONS}{csvfile};

        $self->{LOG}->log($SFHILog::INFO,"Generating CSV File : $csv_file");
        open(OUT,">$csv_file");
        print OUT $$str_ptr;
        close(OUT);
        return;
    }

    if( $self->{OPTIONS}{runondc} eq 'y' )
    {
        require SF::SFDataCorrelator::HostInput;
        SF::SFDataCorrelator::HostInput::importCSVBuffer($$str_ptr,undef);
        return;
    }

    if( !defined $self->{OPTIONS}{server} )
    {
        $self->{LOG}->log($SFHILog::ERROR,"Please specify Server IP to be connected");
        $self->usage();
    }

    # process pkcs12
    $self->{LOG}->log($SFHILog::DEBUG,"Setting up auth certificate");

    $self->{PKCS12_OPTS}{file} = $self->{OPTIONS}{pkcs12} if (defined $self->{OPTIONS}{pkcs12});
    $self->{PKCS12_OPTS}{password} = $self->{OPTIONS}{password} if (defined $self->{OPTIONS}{password});
    my ($crtfile, $keyfile) = SFPkcs12::processPkcs12($self->{PKCS12_OPTS});

    $self->{LOG}->log($SFHILog::INFO,"Connecting to Defense Center : $self->{OPTIONS}{server}");
    # Create the ssl connection to the Host Input Server Daemon
    my $client = SFHIClient::newClient(
                                       $self->{OPTIONS}{server},
                                       $self->{OPTIONS}{port},
                                       $crtfile,
                                       $keyfile,
                                       $self->{OPTIONS}{proto} );
    if( !defined($client) )
    {
        $self->{LOG}->log($SFHILog::ERROR,"Can not Connect to Server: '$self->{OPTIONS}{server}' on port '$self->{OPTIONS}{port}' : Exiting");
        SFPkcs12::cleanUp();
        $self->{LOG}->log($SFHILog::DEBUG,"Can't connect to $self->{OPTIONS}{server} port $self->{OPTIONS}{port}: ".IO::Socket::SSL::errstr()."\n");
        exit(1);
    }
    $self->{CLIENT} = $client;

    my $text;
    my $len = 0;
    my $Version = 1;

    # send version to server
    $self->{LOG}->log($SFHILog::DEBUG,"Send version to server");
    SFHIClient::SendToServer($self->{CLIENT},$SFHIClient::HI_TYPE_VERSION,4,$Version);

    # receive max size from server
    my $max_size = SFHIClient::ReceiveFromServer($self->{CLIENT});
    $sendData_max_size = $max_size;
    $self->{LOG}->log($SFHILog::DEBUG,"MAX Size Received: $max_size");

    # Write CSV data to server
    # We assume hosts are line up in sequence, not randomly located
    my ($line,$host_href,$ip,$next,$offset,$total) = ('',{},'',0,0,length($$str_ptr));
    while($next != -1)
    {
        # get each line
        $next = index($$str_ptr, "\n", $offset);
        if($next == -1) # last line
        {
            $line = substr($$str_ptr,$offset,$total-1);
        }
        elsif($next == 0) # blank line
        {
            # skip over the blank line.
            $offset++;  next;
        }
        else
        {
            # take the next line.
            $line = substr($$str_ptr, $offset, $next+1-$offset);
        }

        if(length($line) > $max_size){
            die "Error:  A line of length ".length($line)." is too big to send: max is $max_size";
        }
        $offset += length($line);

        # Following changes are for customers having large hosts
        if( $line =~ /AddScanResult,([0-9\.]+)/ )
        {
            # ignore invalid IP (syntax error case)
            next if( !$1 );

            $host_href->{$1} = '' if(!defined $host_href->{$1}); # init
            if( $ip ne $1 && $ip ) # done with this IP now
            {
                $self->sendData($host_href->{$ip});
                delete $host_href->{$ip};
            }

            if(length($line) + length($host_href->{$1}) <= $max_size)
            {
                $host_href->{$1} .= $line;
            }
            else
            {
                $self->sendData($host_href->{$1});
                $host_href->{$1} = $line;
            }
            $ip = $1;
        }
        elsif( $line =~ /ScanFlush/ )
        {
            if(length($line) + length($host_href->{$ip}) <= $max_size)
            {
                $host_href->{$ip} .= $line;
            }
            else
            {
                $self->sendData($host_href->{$ip});
                $host_href->{$ip} = $line;
            }
        }
        else
        {
            # send command line by line if it's not AddScanResult
            $self->sendData($line) if($line);
        }
        if ($next == -1)
        {
            $self->sendData($host_href->{$ip}) if($host_href->{$ip});
            $self->flushSendBuffer();
        }
    }
    close($self->{CLIENT});  delete $self->{CLIENT};
    SFPkcs12::cleanUp();
    $self->{LOG}->log($SFHILog::INFO,"Processing Complete");
    #$self->{LOG}->log($SFHILog::DEBUG,"Current Memory Utilization :\n". SFHIClient::mem_report());
}


1;
