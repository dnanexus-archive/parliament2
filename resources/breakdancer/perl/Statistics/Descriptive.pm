package Statistics::Descriptive;

##This module draws heavily from perltoot v0.4 from Tom Christiansen.

require 5.00404;  ##Yes, this is underhanded, but makes support for me easier
		  ##Not only that, but it's the latest "safe" version of
		  ##Perl5.  01-03 weren't bug free.
$VERSION = '2.6';

$Tolerance = 0.0;

use POSIX qw/ceil/;

package Statistics::Descriptive::Sparse;
use strict;
use vars qw($VERSION $AUTOLOAD %fields);
use Carp;

##Define the fields to be used as methods
%fields = (
  count			=> 0,
  mean			=> 0,
  sum			=> 0,
  variance		=> undef,
  pseudo_variance	=> 0,
  min			=> undef,
  max			=> undef,
  mindex		=> undef,
  maxdex		=> undef,
  standard_deviation	=> undef,
  sample_range		=> undef,
  );

sub new {
  my $proto = shift;
  my $class = ref($proto) || $proto;
  my $self = {
    %fields,
    _permitted => \%fields,
  };
  bless ($self, $class);
  return $self;
}

sub add_data {
  my $self = shift;  ##Myself
  my $oldmean;
  my ($min,$mindex,$max,$maxdex);
  my $aref;

  if (ref $_[0] eq 'ARRAY') {
    $aref = $_[0];
  }
  else {
    $aref = \@_;
  }

  ##Take care of appending to an existing data set
  $min    = (defined ($self->{min}) ? $self->{min} : $aref->[0]);
  $max    = (defined ($self->{max}) ? $self->{max} : $aref->[0]);
  $maxdex = $self->{maxdex} || 0;
  $mindex = $self->{mindex} || 0;

  ##Calculate new mean, pseudo-variance, min and max;
  foreach ( @{ $aref } ) {
    $oldmean = $self->{mean};
    $self->{sum} += $_;
    $self->{count}++;
    if ($_ >= $max) {
      $max = $_;
      $maxdex = $self->{count}-1;
    }
    if ($_ <= $min) {
      $min = $_;
      $mindex = $self->{count}-1;
    }
    $self->{mean} += ($_ - $oldmean) / $self->{count};
    $self->{pseudo_variance} += ($_ - $oldmean) * ($_ - $self->{mean});
  }

  $self->{min}          = $min;
  $self->{mindex}       = $mindex;
  $self->{max}          = $max;
  $self->{maxdex}       = $maxdex;
  $self->{sample_range} = $self->{max} - $self->{min};
  if ($self->{count} > 1) {
    $self->{variance}     = $self->{pseudo_variance} / ($self->{count} -1);
    $self->{standard_deviation}  = sqrt( $self->{variance});
  }
  return 1;
}

sub AUTOLOAD {
  my $self = shift;
  my $type = ref($self)
    or croak "$self is not an object";
  my $name = $AUTOLOAD;
  $name =~ s/.*://;     ##Strip fully qualified-package portion
  return if $name eq "DESTROY";
  unless (exists $self->{'_permitted'}->{$name} ) {
    croak "Can't access `$name' field in class $type";
  }
  ##Read only method 
  return $self->{$name};
}

1;

package Statistics::Descriptive::Full;

use Carp;
use strict;
use vars qw(@ISA $a $b %fields);

@ISA = qw(Statistics::Descriptive::Sparse);

##Create a list of fields not to remove when data is updated
%fields = (
  _permitted => undef,  ##Place holder for the inherited key hash
  data       => undef,  ##Our data
  presorted  => undef,  ##Flag to indicate the data is already sorted
  _reserved  => undef,  ##Place holder for this lookup hash
);

##Have to override the base method to add the data to the object
##The proxy method from above is still valid
sub new {
  my $proto = shift;
  my $class = ref($proto) || $proto;
  my $self = $class->SUPER::new();  ##Create my self re SUPER
  $self->{data} = [];   ##Empty array ref for holding data later!
  $self->{'_reserved'} = \%fields;
  $self->{presorted} = 0;
  bless ($self, $class);  #Re-anneal the object
  return $self;
}

sub add_data {
  my $self = shift;
  my $key;
  my $aref;

  if (ref $_[0] eq 'ARRAY') {
    $aref = $_[0];
  }
  else {
    $aref = \@_;
  }
  $self->SUPER::add_data($aref);  ##Perform base statistics on the data
  push @{ $self->{data} }, @{ $aref };
  ##Clear the presorted flag
  $self->{'presorted'} = 0;
  ##Need to delete all cached keys
  foreach $key (keys %{ $self }) { # Check each key in the object
    # If it's a reserved key for this class, keep it
    next if exists $self->{'_reserved'}->{$key};
    # If it comes from the base class, keep it
    next if exists $self->{'_permitted'}->{$key};
    delete $self->{$key};          # Delete the out of date cached key
  }
  return 1;
}

sub get_data {
  my $self = shift;
  return @{ $self->{data} };
}

sub sort_data {
  my $self = shift;
  ##Sort the data in descending order
  $self->{data} = [ sort {$a <=> $b} @{$self->{data}} ];
  $self->presorted(1);
  ##Fix the maxima and minima indices
  $self->{mindex} = 0;
  $self->{maxdex} = $#{$self->{data}};
  return 1;
}

sub presorted {
  my $self = shift;
  if ($@) {  ##Assign
    $self->{'presorted'} = shift;
    return 1;
  }
  else {  ##Inquire
    return $self->{'presorted'};
  }
}

sub percentile {
  my $self = shift;
  my $percentile = shift || 0;
  ##Since we're returning a single value there's no real need
  ##to cache this.

  ##If the requested percentile is less than the "percentile bin
  ##size" then return undef.  Check description of RFC 2330 in the
  ##POD below.
  my $count = $self->{'count'};
  return undef if $percentile < 100 / $count;

  $self->sort_data() unless $self->{'presorted'};
  my $num = $count*$percentile/100;
  my $index = &POSIX::ceil($num) - 1;
  return wantarray
    ?  (${ $self->{data} }[ $index ], $index)
    :   ${ $self->{data} }[ $index ];
}

sub median {
  my $self = shift;

  ##Cached?
  return $self->{median} if defined $self->{median};

  $self->sort_data() unless $self->{'presorted'};
  my $count = $self->{count};
  if ($count % 2) {   ##Even or odd
    return $self->{median} = @{ $self->{data} }[($count-1)/2];
  }
  else {
    return $self->{median} =
	   (@{$self->{data}}[($count)/2] + @{$self->{data}}[($count-2)/2] ) / 2;
  }
}

sub trimmed_mean {
  my $self = shift;
  my ($lower,$upper);
  #upper bound is in arg list or is same as lower
  if (@_ == 1) {
    ($lower,$upper) = ($_[0],$_[0]);
  }
  else {
    ($lower,$upper) = ($_[0],$_[1]);
  }

  ##Cache
  my $thistm = join ':','tm',$lower,$upper;
  return $self->{$thistm} if defined $self->{$thistm};

  my $lower_trim = int ($self->{count}*$lower); 
  my $upper_trim = int ($self->{count}*$upper); 
  my ($val,$oldmean) = (0,0);
  my ($tm_count,$tm_mean,$index) = (0,0,$lower_trim);

  $self->sort_data() unless $self->{'presorted'};
  while ($index <= $self->{count} - $upper_trim -1) {
    $val = @{ $self->{data} }[$index];
    $oldmean = $tm_mean;
    $index++;
    $tm_count++;
    $tm_mean += ($val - $oldmean) / $tm_count;
  }
  return $self->{$thistm} = $tm_mean;
}

sub harmonic_mean {
  my $self = shift;
  return $self->{harmonic_mean} if defined $self->{harmonic_mean};
  my $hs = 0;
  for (@{ $self->{data} }) {
    ##Guarantee that there are no divide by zeros
    return $self->{harmonic_mean} = undef
      unless abs($_) > $Statistics::Descriptive::Tolerance;
    $hs += 1/$_;
  }
  return $self->{harmonic_mean} = undef
    unless abs($hs) > $Statistics::Descriptive::Tolerance;
  return $self->{harmonic_mean} = $self->{count}/$hs;
}

sub mode {
  my $self = shift;
  return $self->{mode} if defined $self->{mode};
  my ($md,$occurances,$flag) = (0,0,1);
  my %count;
  foreach (@{ $self->{data} }) {
    $count{$_}++;
    $flag = 0 if ($count{$_} > 1);
  }
  #Distribution is flat, no mode exists
  if ($flag) {
    return undef;
  }
  foreach (keys %count) {
    if ($count{$_} > $occurances) {
      $occurances = $count{$_};
      $md = $_;
    }
  }
  return $self->{mode} = $md;
}

sub geometric_mean {
  my $self = shift;
  return $self->{geometric_mean} if defined $self->{geometric_mean};
  my $gm = 1;
  my $exponent = 1/$self->{count};
  for (@{ $self->{data} }) {
    return undef if $_ < 0;
    $gm *= $_**$exponent;
  }
  return $self->{geometric_mean} = $gm;
}

sub frequency_distribution {
  my $self = shift;
  my $element;
  my @k = ();
  return undef if $self->{count} < 2; #Must have at least two elements

  ##Cache
  return %{$self->{frequency}}
    if ((defined $self->{frequency}) and !@_);

  my %bins;
  my $partitions = shift;

  if (ref($partitions) eq 'ARRAY') {
    @k = @{ $partitions };
    return undef unless @k;  ##Empty array
    if (@k > 1) {
      ##Check for monotonicity
      $element = $k[0];
      for (@k[1..$#k]) {
	if ($element > $_) {
	  carp "Non monotonic array cannot be used as frequency bins!\n";
	  return undef;
	}
      }
    }
    %bins = map { $_ => 0 } @k;
  }
  else {
    return undef unless $partitions >= 1;
    my $interval = $self->{sample_range}/$partitions;
    my $iter = $self->{min};
    while (($iter += $interval) <  $self->{max}) {
      $bins{$iter} = 0;
      push @k, $iter;  ##Keep the "keys" unstringified
    }
    $bins{$self->{max}} = 0;
    push @k, $self->{max};
  }

  ELEMENT: foreach $element (@{$self->{data}}) {
    for (@k) {
      if ($element <= $_) {
        $bins{$_}++;
        next ELEMENT;
      }
    }
  }
  return %{$self->{frequency}} = %bins;
}

sub least_squares_fit {
  my $self = shift;
  return () if $self->{count} < 2;

  ##Sigma sums
  my ($sigmaxy, $sigmax, $sigmaxx, $sigmayy, $sigmay) = (0,0,0,0,$self->sum);
  my ($xvar, $yvar, $err);

  ##Work variables
  my ($iter,$y,$x,$denom) = (0,0,0,0);
  my $count = $self->{count};
  my @x;

  ##Outputs
  my ($m, $q, $r, $rms);

  if (!defined $_[1]) {
    @x = 1..$self->{count};
  }
  else {
    @x = @_;
    if ( $self->{count} != scalar @x) {
      carp "Range and domain are of unequal length.";
      return ();
    }
  }
  foreach $x (@x) {
    $y = $self->{data}[$iter];
    $sigmayy += $y * $y;
    $sigmaxx += $x * $x;
    $sigmaxy += $x * $y;
    $sigmax  += $x;
    $iter++;
  }
  $denom = $count * $sigmaxx - $sigmax*$sigmax;
  return ()
    unless abs( $denom ) > $Statistics::Descriptive::Tolerance;

  $m = ($count*$sigmaxy - $sigmax*$sigmay) / $denom;
  $q = ($sigmaxx*$sigmay - $sigmax*$sigmaxy ) / $denom;

  $xvar = $sigmaxx - $sigmax*$sigmax / $count;
  $yvar = $sigmayy - $sigmay*$sigmay / $count;

  $denom = sqrt( $xvar * $yvar );
  return () unless (abs( $denom ) > $Statistics::Descriptive::Tolerance);
  $r = ($sigmaxy - $sigmax*$sigmay / $count )/ $denom;

  $iter = 0;
  $rms = 0.0;
  foreach (@x) {
    ##Error = Real y - calculated y
    $err = $self->{data}[$iter] - ( $m * $_ + $q );
    $rms += $err*$err;
    $iter++;
  }

  $rms = sqrt($rms / $count);
  return @{ $self->{least_squares_fit} } = ($q, $m, $r, $rms);
}

1;

package Statistics::Descriptive;

##All modules return true.
1;

__END__

=head1 NAME

Statistics::Descriptive - Module of basic descriptive statistical functions.

=head1 SYNOPSIS

  use Statistics::Descriptive;
  $stat = Statistics::Descriptive::Full->new();
  $stat->add_data(1,2,3,4); $mean = $stat->mean();
  $var  = $stat->variance();
  $tm   = $stat->trimmed_mean(.25);
  $Statistics::Descriptive::Tolerance = 1e-10;

=head1 DESCRIPTION

This module provides basic functions used in descriptive statistics.
It has an object oriented design and supports two different types of
data storage and calculation objects: sparse and full. With the sparse
method, none of the data is stored and only a few statistical measures
are available. Using the full method, the entire data set is retained
and additional functions are available.

Whenever a division by zero may occur, the denominator is checked to be
greater than the value C<$Statistics::Descriptive::Tolerance>, which
defaults to 0.0. You may want to change this value to some small
positive value such as 1e-24 in order to obtain error messages in case
of very small denominators.

Many of the methods (both Sparse and Full) cache values so that subsequent
calls with the same arguments are faster.

=head1 METHODS

=head2 Sparse Methods

=over 5

=item $stat = Statistics::Descriptive::Sparse->new();

Create a new sparse statistics object.

=item $stat->add_data(1,2,3);

Adds data to the statistics variable. The cached statistical values are 
updated automatically.

=item $stat->count();

Returns the number of data items.

=item $stat->mean();

Returns the mean of the data.

=item $stat->sum();

Returns the sum of the data.

=item $stat->variance();

Returns the variance of the data.  Division by n-1 is used.

=item $stat->standard_deviation();

Returns the standard deviation of the data. Division by n-1 is used.

=item $stat->min();

Returns the minimum value of the data set.

=item $stat->mindex();

Returns the index of the minimum value of the data set.

=item $stat->max();

Returns the maximum value of the data set.

=item $stat->maxdex();

Returns the index of the maximum value of the data set.

=item $stat->sample_range();

Returns the sample range (max - min) of the data set.

=back

=head2 Full Methods

Similar to the Sparse Methods above, any Full Method that is called caches
the current result so that it doesn't have to be recalculated.  In some
cases, several values can be cached at the same time.

=over 5

=item $stat = Statistics::Descriptive::Full->new();

Create a new statistics object that inherits from
Statistics::Descriptive::Sparse so that it contains all the methods
described above.

=item $stat->add_data(1,2,4,5);

Adds data to the statistics variable.  All of the sparse statistical
values are updated and cached.  Cached values from Full methods are
deleted since they are no longer valid.  

I<Note:  Calling add_data with an empty array will delete all of your
Full method cached values!  Cached values for the sparse methods are
not changed>

=item $stat->get_data();

Returns a copy of the data array.

=item $stat->sort_data();

Sort the stored data and update the mindex and maxdex methods.  This
method uses perl's internal sort.

=item $stat->presorted(1);

=item $stat->presorted();

If called with a non-zero argument, this method sets a flag that says
the data is already sorted and need not be sorted again.  Since some of
the methods in this class require sorted data, this saves some time.
If you supply sorted data to the object, call this method to prevent
the data from being sorted again. The flag is cleared whenever add_data
is called.  Calling the method without an argument returns the value of
the flag.

=item $x = $stat->percentile(25);

=item ($x, $index) = $stat->percentile(25);

Sorts the data and returns the value that corresponds to the
percentile as defined in RFC2330:

=over 4

=item

For example, given the 6 measurements:

-2, 7, 7, 4, 18, -5

Then F(-8) = 0, F(-5) = 1/6, F(-5.0001) = 0, F(-4.999) = 1/6, F(7) =
5/6, F(18) = 1, F(239) = 1.

Note that we can recover the different measured values and how many
times each occurred from F(x) -- no information regarding the range
in values is lost.  Summarizing measurements using histograms, on the
other hand, in general loses information about the different values
observed, so the EDF is preferred.

Using either the EDF or a histogram, however, we do lose information
regarding the order in which the values were observed.  Whether this
loss is potentially significant will depend on the metric being
measured.

We will use the term "percentile" to refer to the smallest value of x
for which F(x) >= a given percentage.  So the 50th percentile of the
example above is 4, since F(4) = 3/6 = 50%; the 25th percentile is
-2, since F(-5) = 1/6 < 25%, and F(-2) = 2/6 >= 25%; the 100th
percentile is 18; and the 0th percentile is -infinity, as is the 15th
percentile.

Care must be taken when using percentiles to summarize a sample,
because they can lend an unwarranted appearance of more precision
than is really available.  Any such summary must include the sample
size N, because any percentile difference finer than 1/N is below the
resolution of the sample.

=back

(Taken from:
I<RFC2330 - Framework for IP Performance Metrics>,
Section 11.3.  Defining Statistical Distributions.
RFC2330 is available from:
http://www.cis.ohio-state.edu/htbin/rfc/rfc2330.html.)

If the percentile method is called in a list context then it will
also return the index of the percentile.

=item $stat->median();

Sorts the data and returns the median value of the data.

=item $stat->harmonic_mean();

Returns the harmonic mean of the data.  Since the mean is undefined
if any of the data are zero or if the sum of the reciprocals is zero,
it will return undef for both of those cases.

=item $stat->geometric_mean();

Returns the geometric mean of the data.

=item $stat->mode();

Returns the mode of the data. 

=item $stat->trimmed_mean(ltrim[,utrim]);

C<trimmed_mean(ltrim)> returns the mean with a fraction C<ltrim> 
of entries at each end dropped. C<trimmed_mean(ltrim,utrim)> 
returns the mean after a fraction C<ltrim> has been removed from the
lower end of the data and a fraction C<utrim> has been removed from the
upper end of the data.  This method sorts the data before beginning
to analyze it.

All calls to trimmed_mean() are cached so that they don't have to be
calculated a second time.

=item $stat->frequency_distribution($partitions);

=item $stat->frequency_distribution(\@bins);

=item $stat->frequency_distribution();

C<frequency_distribution($partitions)> slices the data into
C<$partition> sets (where $partition is greater than 1) and counts the
number of items that fall into each partition. It returns an
associative array where the keys are the numerical values of the
partitions used. The minimum value of the data set is not a key and the
maximum value of the data set is always a key. The number of entries
for a particular partition key are the number of items which are
greater than the previous partition key and less then or equal to the
current partition key. As an example,

   $stat->add_data(1,1.5,2,2.5,3,3.5,4);
   %f = $stat->frequency_distribution(2);
   for (sort {$a <=> $b} keys %f) {
      print "key = $_, count = $f{$_}\n";
   }

prints

   key = 2.5, count = 4
   key = 4, count = 3

since there are four items less than or equal to 2.5, and 3 items
greater than 2.5 and less than 4.

C<frequency_distribution(\@bins)> provides the bins that are to be used
for the distribution.  This allows for non-uniform distributions as
well as trimmed or sample distributions to be found.  C<@bins> must
be monotonic and contain at least one element.  Note that unless the
set of bins contains the range that the total counts returned will
be less than the sample size.

Calling C<frequency_distribution()> with no arguments returns the last
distribution calculated, if such exists.

=item $stat->least_squares_fit();

=item $stat->least_squares_fit(@x);

C<least_squares_fit()> performs a least squares fit on the data,
assuming a domain of C<@x> or a default of 1..$stat->count().  It
returns an array of four elements C<($q, $m, $r, $rms)> where

=over 4

=item C<$q and $m>

satisfy the equation C($y = $m*$x + $q).

=item C<$r>

is the Pearson linear correlation cofficient.

=item C<$rms>

is the root-mean-square error.

=back

If case of error or division by zero, the empty list is returned.

The array that is returned can be "coerced" into a hash structure
by doing the following:

  my %hash = ();
  @hash{'q', 'm', 'r', 'err'} = $stat->least_squares_fit();

Because calling C<least_squares_fit()> with no arguments defaults
to using the current range, there is no caching of the results.

=back

=head1 REPORTING ERRORS

I read my email frequently, but since adopting this module I've added 2
children and 1 dog to my family, so please be patient about my response
times.  When reporting errors, please include the following to help
me out:

=over 4

=item *

Your version of perl.  This can be obtained by typing perl C<-v> at
the command line.

=item *

Which version of Statistics::Descriptive you're using.  As you can
see below, I do make mistakes.  Unfortunately for me, right now
there are thousands of CD's with the version of this module with
the bugs in it.  Fortunately for you, I'm a very patient module
maintainer.

=item *

Details about what the error is.  Try to narrow down the scope
of the problem and send me code that I can run to verify and
track it down.

=back

=head1 AUTHOR

Colin Kuskie

My email address can be found at http://www.perl.com under Who's Who
or at: http://search.cpan.org/author/COLINK/.

=head1 REFERENCES

RFC2330, Framework for IP Performance Metrics

The Art of Computer Programming, Volume 2, Donald Knuth.

Handbook of Mathematica Functions, Milton Abramowitz and Irene Stegun.

Probability and Statistics for Engineering and the Sciences, Jay Devore.

=head1 COPYRIGHT

Copyright (c) 1997,1998 Colin Kuskie. All rights reserved.  This
program is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.

Copyright (c) 1998 Andrea Spinelli. All rights reserved.  This program
is free software; you can redistribute it and/or modify it under the
same terms as Perl itself.

Copyright (c) 1994,1995 Jason Kastner. All rights
reserved.  This program is free software; you can redistribute it
and/or modify it under the same terms as Perl itself.

=head1 REVISION HISTORY

=item v2.3

Rolled into November 1998

Code provided by Andrea Spinelli to prevent division by zero and to
make consistent return values for undefined behavior.  Andrea also
provided a test bench for the module.

A bug fix for the calculation of frequency distributions.  Thanks to Nick
Tolli for alerting this to me.

Added 4 lines of code to Makefile.PL to make it easier for the ActiveState
installation tool to use.  Changes work fine in perl5.004_04, haven't
tested them under perl5.005xx yet.

=item v2.2

Rolled into March 1998.

Fixed problem with sending 0's and -1's as data.  The old 0 : true ? false
thing.  Use defined to fix.

Provided a fix for AUTOLOAD/DESTROY/Carp bug.  Very strange.

=item v2.1

August 1997

Fixed errors in statistics algorithms caused by changing the
interface.

=item v2.0

August 1997

Fixed errors in removing cached values (they weren't being removed!)
and added sort_data and presorted methods.

June 1997

Transferred ownership of the module from Jason to Colin.

Rewrote OO interface, modified function distribution, added mindex,
maxdex.

=item v1.1

April 1995

Added LeastSquaresFit and FrequencyDistribution.

=item v1.0 

March 1995

Released to comp.lang.perl and placed on archive sites.

=item v.20

December 1994

Complete rewrite after extensive and invaluable e-mail 
correspondence with Anno Siegel.

=item v.10

December 1994

Initital concept, released to perl5-porters list.

=cut
