#!/usr/bin/env perl

use strict;
use warnings;
use Getopt::Std;

&main;

sub main {
	my %opts = (e=>'fermi', t=>2, p=>'fmdef', k=>50);
	getopts('e:t:p:Pck:DBCl:', \%opts);
	$opts{P} = 1 if defined($opts{c});
	$opts{l} = defined($opts{l})? "-l$opts{l}" : "";
	my $min_clean_o = int($opts{k} * 1.2 + .499);

	die(qq/
Usage:   run-fermi.pl [options] <in1.fq> [in2.fq [...]]\n
Options: -P        the input files are paired (ends in separate files)
         -c        the input is collated\/initerleaved FASTQ (two ends in the same file)
         -D        halve the number of jobs for building the split index (effective with -B)
         -B        use the original algorithm for constructing FMD-index (default is BCR)
         -C        skip error correction
         -e FILE   fermi executable [$opts{e}]
         -t INT    number of threads [$opts{t}]
         -p STR    prefix of output files [$opts{p}]
         -l INT    trim reads to INT bp after error correction [inf]
         -k INT    minimum overlap [$opts{k}]
\n/) if (@ARGV == 0);

	my (@lines, $in_list, $fqs, $n_split);

	push(@lines, "FERMI=$opts{e}", "UNITIG_K=$opts{k}", "OVERLAP_K=$min_clean_o", "");
	push(@lines, (defined $opts{P})? "all:$opts{p}.p5.fq.gz" : "all:$opts{p}.p2.mag.gz", "");

	$in_list = join(" ", @ARGV);
	$n_split = defined($opts{D})? $opts{t} : $opts{t} * 2;

	$fqs = '';
	if (defined($opts{P}) && !defined($opts{c})) {
		die if (@ARGV % 2 != 0);
		$fqs = '';
		for (my $i = 0; $i < @ARGV; $i += 2) {
			$fqs .= "\$(FERMI) pe2cofq $ARGV[$i] ".$ARGV[$i+1]."; ";
		}
	} else {
		for my $f (@ARGV) {
			$fqs .= ($f =~ /\.gz$/)? "gzip -dc $f; " : ($f =~ /\.bam$/)? "samtools bam2fq -n $f; " : "cat $f; ";
		}
	}
	chop($fqs); chop($fqs);
	$fqs = '(' . $fqs . ')';

	push(@lines, "# Construct the FM-index for raw sequences");
	my $pre = defined($opts{C})? "$opts{p}.ec" : "$opts{p}.raw";
	if (!defined($opts{B})) {
		push(@lines, "$pre.fmd:$in_list");
		push(@lines, "\t$fqs | \$(FERMI) ropebwt -a bcr -v3 -btNf $pre.tmp - > \$@ 2> \$@.log", '');
	} else {
		push(@lines, "$pre.split.log:$in_list");
		push(@lines, "\t$fqs | \$(FERMI) splitfa - $pre $n_split 2> $pre.split.log\n");
		&build_fmd(\@lines, $n_split, $pre, $opts{t}); # do not trim for the initial index
	}

	if (!defined($opts{C})) {
		push(@lines, "# Error correction");
		push(@lines, "$opts{p}.ec.fq.gz:$opts{p}.raw.fmd");
		push(@lines, "\t$fqs | \$(FERMI) correct -".(defined($opts{P})? 'p' : '')."t $opts{t} $opts{l} \$< - 2> \$@.log | gzip -1 > \$@\n");

		push(@lines, "# Construct the FM-index for corrected sequences");
		$pre = "$opts{p}.ec";
		if (!defined($opts{B})) {
			push(@lines, "$pre.fmd:$opts{p}.ec.fq.gz");
			push(@lines, "\t\$(FERMI) fltuniq \$< 2> $opts{p}.fltuniq.log | \$(FERMI) ropebwt -a bcr -v3 -btf $pre.tmp - > \$@ 2> \$@.log", '');
		} else {
			push(@lines, "$pre.split.log:$opts{p}.ec.fq.gz");
			push(@lines, "\t\$(FERMI) fltuniq \$< 2> $opts{p}.fltuniq.log | \$(FERMI) splitfa - $pre $n_split 2> \$@\n");
			&build_fmd(\@lines, $n_split, $pre, $opts{t});
		}
	}

	push(@lines, "# Generate unitigs");
	if (defined($opts{P})) {
		push(@lines, "$opts{p}.ec.rank:$opts{p}.ec.fmd");
		push(@lines, "\t\$(FERMI) seqrank -t $opts{t} \$< > \$@ 2> \$@.log\n");
		push(@lines, "$opts{p}.p0.mag.gz:$opts{p}.ec.rank $opts{p}.ec.fmd");
		push(@lines, "\t\$(FERMI) unitig -t $opts{t} -l \$(UNITIG_K) -r \$^ 2> \$@.log | gzip -1 > \$@\n");
	} else {
		push(@lines, "$opts{p}.p0.mag.gz:$opts{p}.ec.fmd");
		push(@lines, "\t\$(FERMI) unitig -t $opts{t} -l \$(UNITIG_K) \$< 2> \$@.log | gzip -1 > \$@\n");
	}
	push(@lines, "$opts{p}.p1.mag.gz:$opts{p}.p0.mag.gz");
	push(@lines, "\t\$(FERMI) clean \$< 2> \$@.log | gzip -1 > \$@");
	push(@lines, "$opts{p}.p2.mag.gz:$opts{p}.p1.mag.gz");
	push(@lines, "\t\$(FERMI) clean -CAOFo \$(OVERLAP_K) \$< 2> \$@.log | gzip -1 > \$@\n");

	if (defined($opts{P})) {
		push(@lines, "# Generate scaftigs");
		push(@lines, "$opts{p}.p3.mag.gz:$opts{p}.ec.rank $opts{p}.ec.fmd $opts{p}.p2.mag.gz");
		push(@lines, "\t\$(FERMI) remap -t $opts{t} -r \$^ 2> \$@.log | gzip -1 > \$@");
		push(@lines, "$opts{p}.p4.fa.gz:$opts{p}.ec.fmd $opts{p}.p3.mag.gz");
		push(@lines, qq[\t\$(FERMI) scaf -Pt $opts{t} \$^ `perl -ne 'print "] . '$$1 $$2' . qq[\\n" if /avg = (\\S+) std = (\\S+)/' $opts{p}.p3.mag.gz.log` 2> \$@.log | gzip -1 > \$@\n]);
		push(@lines, "$opts{p}.p5.fq.gz:$opts{p}.ec.rank $opts{p}.ec.fmd $opts{p}.p4.fa.gz");
		push(@lines, qq[\t\$(FERMI) remap -c2 -t $opts{t} -D `perl -ne 'print "] . '$$1' . qq[\\n" if /avg = \\S+ std = \\S+ cap = (\\S+)/' $opts{p}.p3.mag.gz.log` -r \$^ 2> \$@.log | gzip -1 > \$@\n]);
	}
	print join("\n", @lines), "\n";
}

sub build_fmd {
	my ($lines, $t, $pre, $n_threads) = @_;
	my ($logs, $fmds) = ('', '');
	$n_threads ||= $t;
	for (0 .. $t-1) {
		my $p = sprintf("$pre.%.4d", $_);
		$logs .= "$p.fmd.log ";
		$fmds .= "$p.fmd ";
		push(@$lines, "$p.fmd.log:$pre.split.log");
		push(@$lines, "\t\$(FERMI) build -fo $p.fmd $p.fq.gz 2> \$@; rm -f $p.fq.gz");
	}
	push(@$lines, "", "$pre.fmd:$logs");
	push(@$lines, "\t\$(FERMI) merge -t $n_threads -fo \$@ $fmds 2> \$@.log; rm -f $fmds\n");
}
