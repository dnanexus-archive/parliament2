#!/usr/bin/env python

import sys
import argparse
import logging
from breakseq2 import breakseq_index, _version

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate breakpoint library FASTA from breakpoint GFF",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    breakseq_index.add_options(parser)
    parser.add_argument("--reference", help="Reference FASTA", required=True)
    parser.add_argument("--output", help="Output FASTA to generate. Leave unspecified for stdout")
    parser.add_argument("--chromosomes", nargs="+", help="List of chromosomes to process", default=[])
    parser.add_argument('--version', action='version', version='%(prog)s ' + _version.__version__)
    parser.add_argument('--log', help="Log level", default="INFO")

    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: %s' % args.log)

    FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
    logging.basicConfig(level=loglevel, format=FORMAT)

    logger = logging.getLogger(__file__)
    logger.info("Command-line: " + " ".join(sys.argv))
    
    breakseq_index.generate_bplib(args.bplib_gff, args.reference, args.output, args.junction_length, args.format_version, args.chromosomes)
