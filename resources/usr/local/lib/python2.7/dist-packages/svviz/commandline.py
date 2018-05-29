import argparse
import logging
import os
import sys
import tempfile

import svviz
from svviz import demo
from svviz.alignment import AlignmentSet
from svviz.variants import getBreakpointFormatsStr
from svviz.web import checkPortIsClosed

EPILOG = \
"""Breakpoint formats:
{}

For an example, run 'svviz demo'.

Submit bug reports and feature requests at
https://github.com/svviz/svviz/issues"""


def portNumber(string):
    value = int(string)
    if 0 <= value <= 65535:
        return value
    raise argparse.ArgumentTypeError("port must be an integer between 0-65535; got '{}'' instead".format(string))

def converterOptions(value):
    value = value.lower()
    options = ["auto", "librsvg", "webkittopdf", "inkscape", "rsvg-convert"]
    if value in options:
        return value
    raise argparse.ArgumentTypeError("converter must be one of '{}'; got '{}'' instead".format(",".join(options), value))

def setDefault(args, key, default):
    if args.__dict__[key] is None:
        args.__dict__[key] = default

def checkDemoMode(args):
    inputArgs = args[1:]

    if len(inputArgs) < 1:
        return []
    
    if inputArgs[0] == "test":
        inputArgs = "demo 1 -a --no-web".split(" ")

    if "demo" in inputArgs:
        parser = argparse.ArgumentParser(description="svviz version {}".format(svviz.__version__),
            usage="%(prog)s demo [which] [demo options]")

        parser.add_argument("demo")
        parser.add_argument("which", default="1", nargs="?", help=
            "which demo/test to run; pick one of {1,2,3}")
        parser.add_argument("-a", "--auto-download", action="store_true", help=
            "automatically download missing example data without prompting the user")
        parser.add_argument("-n", "--no-web", action="store_true", help=
            "don't show the web interface")
        parser.add_argument("--auto-export", action="store_true", help=
            "export using defaults")

        args, extra_args = parser.parse_known_args(inputArgs)
        if len(extra_args) > 0 or args.demo != "demo":
            print("It looks like you're trying to run one of the demos, but ")
            print("I can't interpret the other arguments you're passing. Try ")
            print("running just 'svviz demo' or 'svviz demo 2'. If you'd like ")
            print("to play with the arguments for the demo, you can first run ")
            print("the simple demo, download the demo data, then copy the ")
            print("command (it's one of the first output lines when you run ")
            print("the demo), and run an edited version of that command. If ")
            print("you need more help, please submit an issue on the github ")
            print("https://github.com/svviz/svviz/issues page.")
            sys.exit(1)

        which = args.which


        if which in ["1","2","3"]:
            which = "example{}".format(which)
        else:
            raise Exception("Don't know how to load this example: {}".format(inputArgs[1]))

        cmd = demo.loadDemo(which, args.auto_download)
        if cmd is not None:
            inputArgs = cmd
            if args.no_web:
                inputArgs.append("--no-web")
            if args.auto_export:
                # put this as a global in demo module so that it persists until we
                # run the "open" command on the file
                demo.TEMPDIR = tempfile.mkdtemp()
                inputArgs.extend(["--export", "{}/temp.pdf".format(demo.TEMPDIR), "-O"])

            logging.info("Running the following command:")
            logging.info("{} {}".format(sys.argv[0], " ".join(inputArgs)))
            logging.info("")
        else:
            raise Exception("couldn't load demo command from info.txt file.")

    return inputArgs

def parseArgs(args):
    inputArgs = checkDemoMode(args)

    epilog = EPILOG.format(getBreakpointFormatsStr())
    
    parser = argparse.ArgumentParser(description="svviz version {}".format(svviz.__version__),
        usage="%(prog)s [options] [demo] [ref breakpoint...] [ref vcf]",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog)

    parser.add_argument("ref", help=
        "reference fasta file (a .faidx index file will be created if it doesn't exist so you need \n"
        "write permissions for this directory)")
    parser.add_argument("breakpoints", nargs="*", help=
        "information about the breakpoint to be analyzed; see below for information")

    requiredParams = parser.add_argument_group("required parameters")
    requiredParams.add_argument("-b", "--bam", action="append", help=
        "sorted, indexed bam file containing reads of interest to plot; can be specified multiple \n"
        "times to load multiple samples")

    inputParams = parser.add_argument_group("input parameters")
    inputParams.add_argument("-t", "--type", help=
        "event type: either del[etion], ins[ertion], inv[ersion], mei (mobile element insertion), \n"
        "tra[nslocation], largedeletion (ldel), breakend (bkend) or batch (for reading variants  \n"
        "from a VCF file in batch mode)")

    inputParams.add_argument("-A", "--annotations", action="append", help=
        "bed or gtf file containing annotations to plot; will be compressed and indexed using \n"
        "samtools tabix in place if needed (can specify multiple annotations files)")

    # Obsolete
    # inputParams.add_argument("-o", "--orientation", help=
    #     "specify orientation of reads or read pairs; should probably be one of the following: \n"
    #     "+-, -+, --, ++ or 'any'; multiple possible orientations can be specified using a \n"
    #     "comma, eg '++,--' (default: infer from input data)")

    inputParams.add_argument("--fasta", help=
        "An additional indexable fasta file specifying insertion sequences (eg mobile element \n"
        "sequences)")

    inputParams.add_argument("-q", "--min-mapq", metavar="MAPQ", default=0, type=float, help=
        "minimum mapping quality for reads (default: 0)")
    inputParams.add_argument("--pair-min-mapq", metavar="PAIR_MAPQ", default=0,
        type=float, help=
        "include only read pairs where at least one read end both exceeds PAIR_MAPQ and \n"
        "falls near the variant being analyzed (default: 0)")
    inputParams.add_argument("--max-multimapping-similarity", metavar="MAX_SIMILARITY", default=0.95,
        type=float, help=
        "maximum ratio between best and second-best alignment scores within visualization \n"
        "region in order to retain read (default: 0.95)")

    inputParams.add_argument("-a", "--aln-quality", metavar="QUALITY", type=float, help=
        "minimum score of the Smith-Waterman alignment against the ref or alt allele in order to be \n"
        "considered (multiplied by 2)")

    inputParams.add_argument("--aln-score-delta", metavar="DELTA", help=
        "minimum difference in scores between ref alignment score and alt alignment score \n"
        "to be assigned to one allele (use an integer to specify a hard score difference \n"
        "threshold, or a float to specify a score difference relative to the read size; \n"
        "default: 2)")

    inputParams.add_argument("--include-supplementary", action="store_true", help=
        "include supplementary alignments (ie, those with the 0x800 bit set in the bam flags); \n"
        "default: false")

    inputParams.add_argument("--fast", action="store_true", help=
        "implements some optimizations designed to find exact sequence matches quickly;\n"
        "will substantially increase speed on Illumina data but may result in some inexact\n"
        "results; default: false")

    inputParams.add_argument("--sample-reads", type=int, help=
        "use at most this many reads (pairs), sampling randomly if need be, useful \n"
        "when running in batch mode (default: use all reads)")

    inputParams.add_argument("--max-reads", type=int, help=
        "maximum number of reads allowed, totaled across all samples, useful when running in batch \n"
        "mode (default: unlimited)")

    inputParams.add_argument("--max-size", type=int, help=
        "maximum event size allowed, totaled across all chromosome parts in bp; if either the ref \n"
        "allele or alt allele exceeds this size, it will be skipped (default: unlimited)")

    inputParams.add_argument("--max-deletion-size", type=int, help=
        "deletion size above which the deletion is analyzed in breakend mode (default: don't \n"
        "convert to breakend mode)")


    interfaceParams = parser.add_argument_group("interface parameters")
    interfaceParams.add_argument("-v", "--version", action="version", 
        version="svviz version {}".format(svviz.__version__), help=
        "show svviz version number and exit")
    interfaceParams.add_argument("-p", "--port", type=portNumber, help=
        "define a port to use for the web browser (default: random port)")
    interfaceParams.add_argument("--processes", type=int, help=
        "how many processes to use for read realignment (default: use all available cores)")
    interfaceParams.add_argument("--no-web", action="store_true", help=
        "don't show the web interface")
    interfaceParams.add_argument("--save-reads", metavar="OUT_BAM_PATH", help=
        "save relevant reads to this file (bam)")

    interfaceParams.add_argument("--verbose", default=3, type=int, help=
        "how verbose the progress and logging should be")

    inputParams.add_argument("--save-state", help=argparse.SUPPRESS)

    interfaceParams.add_argument("-e", "--export", metavar="EXPORT", type=str, help=
        "export view to file; in single variant-mode, the exported file format is determined from \n"
        "the filename extension unless --format is specified; in batch mode, this should be the name \n"
        "of a directory into which to save the files (use --format to set format); setting --export \n"
        "automatically sets --no-web")
    interfaceParams.add_argument("--format", type=str, help="file export format, either svg, png or \n"
        "pdf; by default, this is pdf (batch mode) or automatically identified from the file \n"
        "extension of --export")
    interfaceParams.add_argument("-O", "--open-exported", action="store_true", help=
        "automatically open the exported file")
    interfaceParams.add_argument("--converter", type=converterOptions, help=
        "which program should be used to convert the output into PDF or PNG; choose from [webkitToPDF, \n"
        "librsvg, inkscape] (default: auto)")

    interfaceParams.add_argument("--thicker-lines", action="store_true", help=
        "Reads are shown with thicker lines, potentially overlapping one another, but increasing \n"
        "contrast when zoomed out")
    interfaceParams.add_argument("--context", type=int, default=0, help=
        "Number of additional nucleotides of genomic context to either side of the visualization \n"
        "(useful for showing nearby annotations)")
    interfaceParams.add_argument("-f", "--flanks", action="store_true", help=
        "Show reads in regions flanking the structural variant; these reads do not \n"
        "contribute to the ref or alt allele read counts (default: false)")

    interfaceParams.add_argument("--skip-cigar", action="store_true", help=
        "Don't color mismatches, insertions and deletions")

    interfaceParams.add_argument("--dotplots", action="store_true", help=
        "generate dotplots to show sequence homology within the aligned region; requires some \n"
        "additional optional python libraries (scipy and PIL) and may take several minutes for \n"
        "longer variants")
    interfaceParams.add_argument("--export-insert-sizes", action="store_true", help=
        "plot the insert size distributions for each sample, for each event")

    interfaceParams.add_argument("--summary", metavar="SUMMARY_FILE", help=
        "save summary statistics to this (tab-delimited) file")

    defaults = parser.add_argument_group("presets")
    defaults.add_argument("--pacbio", action="store_true", help=argparse.SUPPRESS)
    defaults.add_argument("--lenient", action="store_true", help=
        "lowers the minimum alignment quality, showing reads even when breakpoints are only \n"
        "approximately correct, or reads of lower quality (eg PacBio); and requires a larger \n"
        "difference in alignment scores in order to assign a read to an allele")

    if len(inputArgs)<1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(inputArgs)
    args._parser = parser

    if not os.path.exists(args.ref):
        print("Could not find fasta file '{}' -- did you forget to specify a reference file?".format(args.ref))
        sys.exit(1)

    if args.pacbio or args.lenient:
        # TODO: should infer this from the input if possible, per-sample
        setDefault(args, "aln_quality", 0.65)
        setDefault(args, "aln_score_delta", 0.005)

    if args.aln_score_delta is None:
        args.aln_score_delta = 2
    try:
        args.aln_score_delta = int(args.aln_score_delta)
    except ValueError:
        try:
            args.aln_score_delta = float(args.aln_score_delta)
        except ValueError:
            logging.error("--aln-score-delta must be an integer or a float")
            sys.exit(1)

    if args.max_reads is not None and args.sample_reads is not None:
        print("Cannot use both --max-reads and --sample-reads options -- pick one!")
        sys.exit(1)
        
    if args.aln_quality is not None:
        AlignmentSet.AlnThreshold = args.aln_quality
    
    if args.export is not None:
        args.no_web = True
        if args.type!="batch" and args.format is None and not args.export.lower()[-3:] in ["svg", "png", "pdf"]:
            print("Export filename must end with one of .svg, .png or .pdf")
            sys.exit(1)
    elif args.format is not None:
        logging.error("ERROR: '--format' option provided without specifying '--export'")
        sys.exit(1)


    if args.port is not None:
        if args.no_web:
            print("--port cannot be used with --no-web or --export")
            sys.exit(1)
        if not checkPortIsClosed(args.port):
            print("Error: port {} is already in use!".format(args.port))
            sys.exit(1)

    logging.info(str(args))
    return args

if __name__ == '__main__':
    print(parseArgs())