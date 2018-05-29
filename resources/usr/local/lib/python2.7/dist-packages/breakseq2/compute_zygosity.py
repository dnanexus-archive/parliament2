#!/usr/bin/env python

import sys
import pysam
import argparse

DEFAULT_MIN_OVERLAP = 10
DEFAULT_WINDOW = 100

def add_options(main_parser):
    local_parser = main_parser.add_argument_group("Zygosity computation options")
    local_parser.add_argument("--window", help="Window size", type=int, default=DEFAULT_WINDOW)
    local_parser.add_argument("--min_overlap", help="Min overlap", type=int,
                        default=DEFAULT_MIN_OVERLAP)


def is_good_candidate(aln, location, min_overlap):
    if aln.is_unmapped: return False
    if aln.mapq < 1: return False
    lspan = location - aln.pos
    rspan = aln.aend - location
    return min(lspan, rspan) >= min_overlap


def line_to_tuple(line):
    line = line.strip()
    line_items = line.split("\t")
    return tuple(line_items[0:3]) + (int(line_items[3]), int(line_items[4])) + tuple(line_items[5:])


def compute_zygosity(input_files, window, input_gff, output, min_overlap=DEFAULT_MIN_OVERLAP):
    input_handle = sys.stdin if input_gff == "-" else open(input_gff)
    lines = map(line_to_tuple, input_handle.readlines())

    sam_file_handles = []
    for input_file in input_files:
        sam_file = pysam.Samfile(input_file, "r" + ("" if input_file.endswith("sam") else "b"))
        sam_file_handles.append(sam_file)

    outfd = open(output, "w") if output else sys.stdout
    for line_items in lines:
        chromosome, tool, sv_type, start, end = line_items[0:5]

        counts = []
        location_list = [start - 1]
        if sv_type == "Deletion": location_list.append(end)
        for location in location_list:
            count = 0
            for sam_file in sam_file_handles:
                iterator = sam_file.fetch(reference=chromosome, start=location - window,
                                          end=location - min_overlap + 1)
                for aln in iterator:
                    if not is_good_candidate(aln, location, min_overlap): continue
                    count = count + 1
            counts.append(count)
        genotype = "0/1" if sum(counts) >= 2 else "1/1"
        outfd.write("%s;GT %s;COUNTS %s\n" % ("\t".join(map(str, line_items)), genotype, ",".join(map(str, counts))))

    for sam_file in sam_file_handles:
        sam_file.close()
    if output: outfd.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract well-mapped reads around a location",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    add_options(parser)

    # Add input/output options
    parser.add_argument("--input_bams", nargs="+", help="Input BAMs", required=True)
    parser.add_argument("--input_gff", help="GFF for genotyping", required=True)
    parser.add_argument("--output", help="Output GFF with genotypes. Leave unspecified for stdout")

    args = parser.parse_args()
    compute_zygosity(args.input_bams, args.window, args.input_gff, args.output, args.min_overlap)