package SFHILog;

use strict;
use warnings;

our ($ERROR,$WARNING,$INFO,$DEBUG) = (0,1,2,3);

my $levels =
{
    $ERROR => {
        str         => "ERROR",
        syslog_type => "err"
    },
    $WARNING => {
        str         => "WARNING",
        syslog_type => "warning"
    },
    $INFO => {
        str         => "INFO",
        syslog_type => "info"
    },
    $DEBUG => {
        str         => "DEBUG",
        syslog_type => "debug"
    },
};

sub new
{
    my $class = shift;
    my ($log_params) = @_;

    my $self;

    $self->{SYSLOG} = $log_params->{syslog};
    $self->{STDERR} = $log_params->{stderr};

    $self->{LOGFILE} = $log_params->{logfile};
    $self->{LOGLEVEL} = $INFO;
    $self->{LOGLEVEL} = $log_params->{loglevel} if defined($log_params->{loglevel});
    $self->{PLUGIN} = $log_params->{plugin};

    if( $log_params->{syslog} )
    {
        # we may not find Sys::Syslog (like for Windows system).
        # in this case, we just disable syslog and do stderr
        eval "use Sys::Syslog qw( :DEFAULT setlogsock)";
        if ($@)
        {
            $self->{STDERR} = 1;
            $self->{SYSLOG} = 0;
            $self->{LOGFILE} = './ScanAgent.log' if(!defined($self->{LOGFILE}));
            warn "*** Sys::Syslog is NOT available, Logging to STDERR and default logfile: ScanAgent.log ***\n";
        }
        else
        {
            setlogsock('unix');
        }
    }
    $self->{STDERR} = 1 if(!$self->{SYSLOG} && !$self->{STDERR} && !$self->{LOGFILE});
    bless $self, $class;
    return $self;
}

sub log
{
    my ($self,$level,$str,$layer) = @_;

    $layer = 0 if(!defined($layer));
    my $date = scalar(localtime());
    my ($package,$file,$line) = caller($layer);

    my $message = "[$levels->{$level}{str}] $str";
    $message .= " [$file,$line]" if ($self->{LOGLEVEL} == $DEBUG);

    if( $self->{SYSLOG} && $level <= $self->{LOGLEVEL} )
    {
        openlog($self->{PLUGIN}.' ','pid,cons','user');
        syslog($levels->{$level}{syslog_type},$message);
        closelog();
    }

    $message = $date ." ". $message ."\n";

    if( $self->{STDERR} && $level <= $self->{LOGLEVEL} )
    {
        warn $message;
    }
    if( $self->{LOGFILE} && $level <= $self->{LOGLEVEL} )
    {
        my $sdlog = undef;
        open($sdlog,">>$self->{LOGFILE}");
        print $sdlog $message;
        close($sdlog);
    }
}

1;
