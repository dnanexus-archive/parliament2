#!/usr/bin/env python

import pysam
import argparse
import sys
import time
import logging
import multiprocessing

DEFAULT_MIN_SOFT_CLIP=20
DEFAULT_MIN_SOFT_CLIP_MAPQ=10
DEFAULT_MIN_SOFT_CLIP_MATE_MAPQ=10
DEFAULT_BAD_MAP_MAX_SOFT_CLIP=50
DEFAULT_BAD_MAP_MIN_MAPQ=10
DEFAULT_BAD_MAP_MIN_MATE_MAPQ=10
DEFAULT_BAD_MAP_MIN_NM=8


def add_options(main_parser):
    local_parser = main_parser.add_argument_group("Read extraction options.")
    local_parser.add_argument('--min_soft_clip', default=DEFAULT_MIN_SOFT_CLIP,
                        help="Minimum soft-clipping for a read to be considered heavily soft-clipped", type=int)
    local_parser.add_argument('--min_soft_clip_mapq', default=DEFAULT_MIN_SOFT_CLIP_MAPQ,
                        help="Min mapping quality of a heavily soft-clipped read to be considered for junction-mapping",
                        type=int)
    local_parser.add_argument('--min_soft_clip_mate_mapq', default=DEFAULT_MIN_SOFT_CLIP_MATE_MAPQ,
                        help="Min mapping quality of the mate of a heavily soft-clipped read to be considered for junction-mapping",
                        type=int)
    local_parser.add_argument('--bad_map_max_soft_clip', default=DEFAULT_BAD_MAP_MAX_SOFT_CLIP,
                        help="Maximum soft-clip for a read to be considered badly-mapped and, therefore, used for junction-mapping",
                        type=int)
    local_parser.add_argument('--bad_map_min_mapq', default=DEFAULT_BAD_MAP_MIN_MAPQ,
                        help="Minimum mapping quality of a read to considered badly-mapped", type=int)
    local_parser.add_argument('--bad_map_min_nm', default=DEFAULT_BAD_MAP_MIN_NM,
                        help="Min edit distance for a read to be considered badly mapped", type=int)
    local_parser.add_argument('--bad_map_min_mate_mapq', default=DEFAULT_BAD_MAP_MIN_MATE_MAPQ,
                        help="Minimum mapping quality of the mate of a badly mapped read to be considered for junction-mapping",
                        type=int)
    local_parser.add_argument('--bams', nargs='+', help="BAMs", required=True)
    local_parser.add_argument('--chromosome', help="Chromosome to process. Leave unspecified to include all")
    local_parser.add_argument('--out', help="Output file. Leave unspecified for stdout.")


def is_good_candidate(aln, min_soft_clip, min_soft_clip_mapq, min_soft_clip_mate_mapq, bad_map_max_soft_clip,
                      bad_map_min_mapq, bad_map_min_nm, bad_map_min_mate_mapq):
    if aln.is_duplicate or aln.is_secondary: return False
    if aln.is_unmapped: return True
    # some tweaking may be required to ensure the reads in a pair are used consistently
    if aln.cigar is None: return False
    tags = aln.tags
    nm = int(aln.opt("NM"))
    xm = int(aln.opt("XM")) if "XM" in tags else 0
    mq = int(aln.opt("MQ")) if "MQ" in tags else 30
    max_soft_clip = 0
    max_del = 0
    for (op, length) in aln.cigar:
        if op == 4:
            max_soft_clip = max(max_soft_clip, length)
        elif op == 2:
            max_del = max(max_del, length)
    if (
            max_soft_clip >= min_soft_clip or max_del >= min_soft_clip) and aln.mapq >= min_soft_clip_mapq and xm == 0 and mq >= min_soft_clip_mate_mapq: return True
    if (
            max_soft_clip <= bad_map_max_soft_clip or max_del <= bad_map_max_soft_clip) and aln.mapq >= bad_map_min_mapq and nm >= bad_map_min_nm and mq >= bad_map_min_mate_mapq: return True
    return False


def get_iterator(bam_handle, chromosome):
    if chromosome is None:
        return bam_handle
    if chromosome:
        return bam_handle.fetch(chromosome)

    # Get the iterator for the reads with no coordinates
    bam_header = bam_handle.header
    for bam_chr_dict in bam_header['SQ'][::-1]:
        chr_name = bam_chr_dict['SN']
        chr_length = bam_chr_dict['LN']
        if bam_handle.count(chr_name) > 0:
            bam_handle.fetch(chr_name)
            return bam_handle
    bam_handle.reset()
    return bam_handle


def print_candidate_reads(bams, chromosome, min_soft_clip=DEFAULT_MIN_SOFT_CLIP, min_soft_clip_mapq=DEFAULT_MIN_SOFT_CLIP_MAPQ, min_soft_clip_mate_mapq=DEFAULT_MIN_SOFT_CLIP_MATE_MAPQ, bad_map_max_soft_clip=DEFAULT_BAD_MAP_MAX_SOFT_CLIP,
                          bad_map_min_mapq=DEFAULT_BAD_MAP_MIN_MAPQ, bad_map_min_nm=DEFAULT_BAD_MAP_MIN_NM, bad_map_min_mate_mapq=DEFAULT_BAD_MAP_MIN_MATE_MAPQ, outfile=None):
    func_logger = logging.getLogger("%s-%s" % (print_candidate_reads.__name__, multiprocessing.current_process()))
    start_time = time.time()

    outfd = sys.stdout if outfile is None else open(outfile, "w")
    readcount = 0
    for input_file in bams:
        sam_file = pysam.Samfile(input_file, "r" + ("" if input_file.endswith("sam") else "b"))
        iterator = get_iterator(sam_file, chromosome)
        for aln in iterator:
            if not is_good_candidate(aln, min_soft_clip, min_soft_clip_mapq, min_soft_clip_mate_mapq,
                                     bad_map_max_soft_clip, bad_map_min_mapq, bad_map_min_nm,
                                     bad_map_min_mate_mapq): continue
            read_id = aln.qname
            if aln.is_paired and not aln.mate_is_unmapped:
                read_id = read_id + "$" + sam_file.getrname(aln.rnext)
            outfd.write("@%s\n%s\n+\n%s\n" % (read_id, aln.seq, aln.qual))
            readcount += 1
        sam_file.close()

    if outfile is not None:
        outfd.close()

    func_logger.info("Extracted %d reads from BAMs %s for chromosome %s (%g s)" % (readcount, ", ".join(map(str, bams)), str(chromosome), time.time() - start_time))
    return readcount

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Select reads for junction mapping: unmapped reads, heavily soft-clipped reads and badly mapped reads are selected for junction-mapping in later stages",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_options(parser)

    args = parser.parse_args()

    print_candidate_reads(args.bams, args.chromosome, args.min_soft_clip, args.min_soft_clip_mapq, args.min_soft_clip_mate_mapq, args.bad_map_max_soft_clip,
                          args.bad_map_min_mapq, args.bad_map_min_nm, args.bad_map_min_mate_mapq, outfile=args.out)
