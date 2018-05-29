#!/usr/bin/env python

import argparse, sys
from argparse import RawTextHelpFormatter
from collections import defaultdict
import pysam

__author__ = "Author (email@site.com)"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2013-05-09 14:31 $"

# --------------------------------------
# define functions

def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
bamlibs.py\n\
author: " + __author__ + "\n\
version: " + __version__ + "\n\
description: output comma delimited string of read group IDs for each library")
    parser.add_argument('-S', '--is_sam', required=False, action='store_true', help='input is SAM')
    parser.add_argument('input', nargs='?', type=str, default=None,
                        help='SAM/BAM file to inject header lines into. If \'-\' or absent then defaults to stdin.')

    # parse the arguments
    args = parser.parse_args()

    # if no input, check if part of pipe and if so, read stdin.
    if args.input == None:
        if sys.stdin.isatty():
            parser.print_help()
            exit(1)
        else:
            args.input = '-'

    # send back the user input
    return args

# add read group info to header of new sam file
def get_libs(bam, is_sam, header_only):
    if is_sam:
        in_bam = pysam.Samfile(bam, 'r', check_sq=False)
    else:
        in_bam = pysam.Samfile(bam, 'rb', check_sq=False)

    lib_rg = defaultdict(list)
    for line in in_bam.text.split('\n'):
        if line[:3]!="@RG":
            continue
        v = line.rstrip().split('\t')
        rg_lib = "" # default to no library
        for tag in v:
            if tag[:3]=="ID:":
                rg_id = tag[3:]
            elif tag[:3] =="LB:":
                rg_lib = tag[3:]
        lib_rg[rg_lib].append(rg_id)

    # print
    for lib in lib_rg:
        print ','.join(lib_rg[lib])
    in_bam.close()

    return

# --------------------------------------
# main function

def main():
    # parse the command line args
    args = get_args()

    # clean the header
    get_libs(args.input, args.is_sam, True)

# initialize the script
if __name__ == '__main__':
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32:  # ignore SIGPIPE
            raise
