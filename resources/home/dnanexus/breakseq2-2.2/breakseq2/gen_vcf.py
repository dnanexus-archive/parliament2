#!/usr/bin/env python

import sys
import argparse
import pysam


def add_options(main_parser):
    pass


def get_contigs(fai_filename):
    fai_file = open(fai_filename)
    contigs = {}
    contigs_order = {}
    linenum = 0
    for line in fai_file.readlines():
        line = line.strip()
        line_items = line.split("\t")
        name, length = line_items[0:2]
        name = name.split(" ")[0]
        contigs[name] = int(length)
        contigs_order[name] = linenum
        linenum += 1
    fai_file.close()
    return contigs, contigs_order


def line_to_tuple(line):
    line = line.strip()
    line_items = line.split("\t")
    info_items = line_items[8].split(";")
    info_dict = dict([info_item.split(" ") for info_item in info_items])

    return tuple(line_items[0:3]) + (int(line_items[3]), int(line_items[4])) + (info_dict,)


def gff_to_vcf(reference, input_gff, sample, output, no_ref_allele=True, compress=True):
    fasta_handle = pysam.Fastafile(reference)

    contigs, contigs_order = get_contigs(reference + ".fai")
    contig_names = contigs.keys()
    contig_names.sort(key=lambda tup: contigs_order[tup])

    input_handle = sys.stdin if input_gff == "-" else open(input_gff)
    lines = map(line_to_tuple, input_handle.readlines())
    lines.sort(key=lambda tup: (contigs_order[tup[0]], tup[3], tup[4], tup[2], tup[1]))

    contig_str = ""
    for contig_name in contig_names:
        contig_str += "##contig=<ID=%s,length=%d>\n" % (contig_name, contigs[contig_name])

    outfd = open(output, "w") if output else sys.stdout
    outfd.write("""##fileformat=VCFv4.1
##reference=%s
##INFO=<ID=BKPTID,Number=.,Type=String,Description=\"ID of the assembled alternate allele in the assembly file\">
##INFO=<ID=CIEND,Number=2,Type=Integer,Description=\"Confidence interval around END for imprecise variants\">
##INFO=<ID=CIPOS,Number=2,Type=Integer,Description=\"Confidence interval around POS for imprecise variants\">
##INFO=<ID=END,Number=1,Type=Integer,Description=\"End position of the variant described in this record\">
##INFO=<ID=HOMLEN,Number=.,Type=Integer,Description=\"Length of base pair identical micro-homology at event breakpoints\">
##INFO=<ID=HOMSEQ,Number=.,Type=String,Description=\"Sequence of base pair identical micro-homology at event breakpoints\">
##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description=\"Imprecise structural variation\">
##INFO=<ID=MEINFO,Number=4,Type=String,Description=\"Mobile element info of the form NAME,START,END,POLARITY\">
##INFO=<ID=SVLEN,Number=.,Type=Integer,Description=\"Difference in length between REF and ALT alleles\">
##INFO=<ID=SVTYPE,Number=1,Type=String,Description=\"Type of structural variant\">
##FILTER=<ID=LowQual,Description=\"Low Quality\">
%s##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">
##FORMAT=<ID=ABC,Number=.,Type=Integer,Description=\"Counts of different junction types (A=left insertion, B=right insertion, C=deletion)\">
##FORMAT=<ID=PE,Number=1,Type=Integer,Description=\"Paired-end read support for SV\">
##FORMAT=<ID=REFCOUNTS,Number=.,Type=Integer,Description=\"Reads supporting reference allele\">
##ALT=<ID=DEL,Description=\"Deletion\">
##ALT=<ID=DEL:ME:ALU,Description=\"Deletion of ALU element\">
##ALT=<ID=DEL:ME:L1,Description=\"Deletion of L1 element\">
##ALT=<ID=DUP,Description=\"Duplication\">
##ALT=<ID=DUP:TANDEM,Description=\"Tandem Duplication\">
##ALT=<ID=INS,Description=\"Insertion of novel sequence\">
##ALT=<ID=INS:ME:ALU,Description=\"Insertion of ALU element\">
##ALT=<ID=INS:ME:L1,Description=\"Insertion of L1 element\">
##ALT=<ID=INV,Description=\"Inversion\">
##ALT=<ID=CNV,Description=\"Copy number variable region\">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t%s\n""" % (reference, contig_str, sample))
    for line_items in lines:
        chromosome, tool, sv_type, start, end, info_dict = line_items
        qual = info_dict["QUAL"] if "QUAL" in info_dict else "."
        svlen = int(info_dict["SVLEN"]) if "SVLEN" in info_dict else 0
        gt = info_dict["GT"] if "GT" in info_dict else "./."
        abc = info_dict["ABC"] if "ABC" in info_dict else "0,0,0"
        pe = info_dict["PE"] if "PE" in info_dict else "0"
        refcounts = info_dict["COUNTS"] if "COUNTS" in info_dict else "0"

        qual = qual if qual == "LowQual" else "PASS"

        if sv_type == "Deletion":
            if not no_ref_allele:
                ref_allele = fasta_handle.fetch(chromosome, start - 2, end)
            else:
                ref_allele = fasta_handle.fetch(chromosome, start - 2, start - 1)
            alt_allele = ref_allele[0:1] if not no_ref_allele else "<DEL>"
            info = "SVLEN=%d;SVTYPE=DEL;END=%d" % (-svlen, end)
            outfd.write(
                "%s\t%d\t.\t%s\t%s\t.\t%s\t%s\tGT:ABC:PE:REFCOUNTS\t%s:%s:%s:%s\n" % (chromosome, start - 1, ref_allele, alt_allele, qual, info, gt, abc, pe, refcounts))
        elif sv_type == "Insertion":
            ref_allele = fasta_handle.fetch(chromosome, start - 2, start - 1)
            alt_allele = "<INS>"
            info = "SVLEN=%d;SVTYPE=INS;END=%d" % (svlen, start - 1)
            outfd.write(
                "%s\t%d\t.\t%s\t%s\t.\t%s\t%s\tGT:ABC:PE:REFCOUNTS\t%s:%s:%s:%s\n" % (chromosome, start - 1, ref_allele, alt_allele, qual, info, gt, abc, pe, refcounts))

    fasta_handle.close()
    if output:
        outfd.close()
        if compress:
            pysam.tabix_index(output, force=True, preset="vcf")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert BreakSeq2 GFF to VCF", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--input_gff", metavar="input_gff", help="Input GFF", required=False, default="-")
    parser.add_argument("--sort", action="store_true", help="Sort GFF")
    parser.add_argument("--reference", metavar="reference", help="Reference file", required=True)
    parser.add_argument("--sample", metavar="Sample", help="Sample name", required=True)
    parser.add_argument("--no_ref_allele", action="store_true", help="Disable ref allele sequence")
    parser.add_argument("--output", help="Output VCF. Leave unspecified for stdout")

    args = parser.parse_args()

    gff_to_vcf(args.reference, args.input_gff, args.sample, args.output, args.no_ref_allele)



