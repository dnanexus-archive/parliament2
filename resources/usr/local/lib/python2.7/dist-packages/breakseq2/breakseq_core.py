#!/usr/bin/env python

import sys
import pysam
import argparse
import logging

DEFAULT_MIN_SPAN = 10


def add_options(main_parser):
    local_parser = main_parser.add_argument_group("BreakSeq core options")
    local_parser.add_argument("--min_span", help="Minimum span for junction", type=int, default=DEFAULT_MIN_SPAN)


def is_unique(aln):
    if aln.is_unmapped or aln.is_secondary or aln.is_duplicate:
        return False
    tags = aln.tags
    utags = ['X0']
    hits = 0
    for tname, tvalue in tags:
        if tname in utags:
            hits += tvalue
    return hits == 1


cigars = ['M', 'I', 'D', 'N', 'S', 'H', 'P', '=', 'X']


def to_cigar(c):
    cigar = ""
    for k, v in c:
        cigar += str(v) + cigars[k]
    return cigar


def breakseq_core(input_files, output, min_span=DEFAULT_MIN_SPAN, chromosomes=[]):
    func_logger = logging.getLogger(breakseq_core.__name__)

    outfd = open(output, "w") if output else sys.stdout
    outfd.write("#chr\tsrc\tevent\tstart\tend\tscore\tstrand\tjunct\tattribute\n")

    count = 0
    for input_file in input_files:
        func_logger.info("Processing %s" % input_file)
        sam_file = pysam.Samfile(input_file, "r" + ("" if input_file.endswith("sam") else "b"))
        lib_lens = {}
        for i in range(len(sam_file.references)):
            lib_lens[sam_file.references[i]] = sam_file.lengths[i]

        for aln in sam_file:
            if not is_unique(aln):
                continue
            j = sam_file.getrname(aln.tid)
            j_fields = j.replace("-", ":").split(":")
            if len(j_fields) == 5:
                jchr, jstart, jend, src, junct = j_fields
                sv_length = int(jend) - int(jstart) if junct == "C" else 0
                sv_type = "Deletion" if junct == "C" else "Insertion"
            else:
                # Latest breakpoint library has length and SV type also encoded in the name
                jchr, jstart, jend, src, sv_type, sv_length, junct = j_fields

            ichr = None if aln.qname.find("$") < 0 else aln.qname.split("$")[-1]

            if chromosomes and jchr not in chromosomes:
                continue

            pe = "-"
            if ichr is not None:
                if ichr == jchr:
                    pe = "Y"
                else:
                    continue

            lib_len = lib_lens[j]

            lspan = lib_len / 2 - aln.pos
            rspan = aln.aend - lib_len / 2

            if min(lspan, rspan) < min_span:
                continue
            else:
                outfd.write("\t".join([jchr, src, sv_type, jstart, jend, "1", ".",
                                       junct]) + "\tNAME %s;MAPQ %s;CIGAR %s;POS %s;END %s;LIBLEN %s;LSPAN %s;RSPAN %s;PE %s;SVLEN %s\n" % (
                                aln.qname, aln.mapq, aln.cigarstring, aln.pos, aln.aend, lib_len, lspan, rspan, pe,
                                sv_length))
                count += 1
        sam_file.close()

    if output: outfd.close()

    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="BreakSeq2 core",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    add_options(parser)
    parser.add_argument("--input_bams", help="BAM consisting of reads aligned to the breakpoint library", nargs="+", required=True)
    parser.add_argument("--output", help="Output file")

    args = parser.parse_args()

    FORMAT = '%(levelname)s %(asctime)-15s %(name)-20s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    logger = logging.getLogger(__name__)

    breakseq_core(args.input_bams, args.output, args.min_span)

