#!/usr/bin/env python

import argparse
import logging
import os
import sys
from breakseq2 import breakseq_top

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="BreakSeq2: Ultrafast and accurate nucleotide-resolution analysis of structural variants",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    breakseq_top.add_options(parser)

    args = parser.parse_args()

    FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    logger = logging.getLogger(__file__)
    logger.info("Command-line: " + " ".join(sys.argv))

    sys.exit(breakseq_top.breakseq2_workflow(args.sample, args.bplib, args.bplib_gff, os.path.realpath(args.bwa),
                                             os.path.realpath(args.samtools), args.bams, os.path.realpath(args.work),
                                             args.chromosomes,
                                             args.nthreads, args.min_span, args.min_overlap,
                                             os.path.realpath(args.reference),
                                             args.keep_temp, args.window, args.junction_length))
