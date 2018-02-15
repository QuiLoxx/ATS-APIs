package SFCheckPreReq;

use strict;

sub assertModules
{
    my $modules = shift;

    my $results;
    $results = { missing => [],
                 found => []
               };

    foreach my $module (sort @{$modules})
    {
        eval "require $module";
        if ($@)
        {
            push @{$results->{missing}}, $module;
        }
        else
        {
            push @{$results->{found}}, $module;
        }
    }

    if (scalar(@{$results->{missing}}) > 0)
    {
        print "\nThe following prerequisite Perl modules are missing :\n";
        foreach my $miss (@{$results->{missing}}) {
            print "\t$miss\n";
        }
        print "\n";
        exit(1);
    }
}

1;
