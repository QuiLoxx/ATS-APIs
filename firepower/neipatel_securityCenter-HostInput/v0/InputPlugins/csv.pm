package InputPlugins::csv;

use strict;
use warnings;

BEGIN
{
    use SFCheckPreReq;
    SFCheckPreReq::assertModules(['YAML::XS']);
}

use YAML::XS qw(LoadFile);

# info hash containing plugin information
my $info = {
    init => \&init,
    input => \&input,
    description => "Handles CSV files",
    info => "<CSV File Imported>",
};


# called for every plugin at program initialization time
sub register{
    return $info;
}

# called if this plugin is selected.  $opts contains the filename to parse.
sub init{

    my ($opts) = @_;

    return 0 if( $opts->{multiinfo} );

    my $filename;
    if( $opts->{plugininfo} )
    {
        $filename = $opts->{plugininfo};
    }
    die "Input filename is required" if( !defined($filename) );

    open IN, "<", $filename or die "Unable to open $filename for reading";

    return 0;
}

# read the input file and return CSV
sub input{
    my $str = '';

    while(my $line = <IN>)
    {
        $str .= $line;
    }
    return \$str;
}

1;
