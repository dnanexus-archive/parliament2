#!/usr/bin/env python

import argparse
import subprocess
import gzip


def parse_arguments():
    args = argparse.ArgumentParser(description='Parliament2')
    args.add_argument('--bam', required=True, help="The name of the Illumina BAM file for which to call structural variants containing mapped reads.")
    args.add_argument('--bai', required=False, help="(Optional) The name of the corresponding index for the Illumina BAM file.")
    args.add_argument('--gatk_jar', required=True, help="GATK3 jar file to use for IndelRealigner.")
    args.add_argument('-r', '--ref_genome', required=True, help="The name of the reference file that matches the reference used to map the Illumina inputs.")
    args.add_argument('--prefix', required=False, help="(Optional) If provided, all output files will start with this. If absent, the base of the BAM file name will be used.")
    args.add_argument('--filter_short_contigs', action="store_true", help="If selected, SV calls will not be generated on contigs shorter than 1 MB.")
    args.add_argument('--breakdancer', action="store_true", help="If selected, the program Breakdancer will be one of the SV callers run.")
    args.add_argument('--breakseq', action="store_true", help="If selected, the program BreakSeq2 will be one of the SV callers run.")
    args.add_argument('--manta', action="store_true", help="If selected, the program Manta will be one of the SV callers run.")
    args.add_argument('--cnvnator', action="store_true", help="If selected, the program CNVnator will be one of the SV callers run.")
    args.add_argument('--lumpy', action="store_true", help="If selected, the program Lumpy will be one of the SV callers run.")
    args.add_argument('--delly_deletion', action="store_true", help="If selected, the deletion module of the program Delly2 will be one of the SV callers run.")
    args.add_argument('--delly_insertion', action="store_true", help="If selected, the insertion module of the program Delly2 will be one of the SV callers run.")
    args.add_argument('--delly_inversion', action="store_true", help="If selected, the inversion module of the program Delly2 will be one of the SV callers run.")
    args.add_argument('--delly_duplication', action="store_true", help="If selected, the duplication module of the program Delly2 will be one of the SV callers run.")
    args.add_argument('--genotype', action="store_true", help="If selected, candidate events determined from the individual callers will be genotyped and merged to create a consensus output.")
    args.add_argument('--atlas', action="store_true", help="If selected, xAtlas will be run as a SNP and Indel caller.")
    args.add_argument('--stats', action="store_true", help="If selected, samtools flagstat will be run to gather statistics on the input BAM file.")
    args.add_argument('--svviz', action="store_true", help="If selected, visualizations of genotyped SV events will be produced with SVVIZ, one screenshot of support per event. For this option to take effect, Genotype must be selected.")
    args.add_argument('--svviz_only_validated_candidates', action="store_true", help="Run SVVIZ only on validated candidates? For this option to be relevant, SVVIZ must be selected. NOT selecting this will make the SVVIZ component run longer.")
    args.add_argument('--dnanexus', action="store_true", help=argparse.SUPPRESS)

    return args.parse_args()


def gunzip_input(input_file):
    if input_file.endswith('.gz'):
        subprocess.check_call(['gunzip', input_file])
        return input_file[:-3]
    else:
        return input_file


def run_parliament(bam, bai, gatk_jar, ref_genome, prefix, filter_short_contigs, breakdancer, breakseq, manta, cnvnator, lumpy, delly_deletion, delly_insertion, delly_inversion, delly_duplication, genotype, atlas, stats, svviz, svviz_only_validated_candidates):

    if bai is not None:    
        subprocess.check_call(['bash', 'parliament2.sh', bam, bai, gatk_jar, ref_genome, prefix, str(filter_short_contigs), str(breakdancer), str(breakseq), str(manta), str(cnvnator), str(lumpy), str(delly_deletion), str(delly_insertion), str(delly_inversion), str(delly_duplication), str(genotype), str(atlas), str(stats), str(svviz), str(svviz_only_validated_candidates)])
    else:
        subprocess.check_call(['bash', 'parliament2.sh', bam, "None", gatk_jar, ref_genome, prefix, str(filter_short_contigs), str(breakdancer), str(breakseq), str(manta), str(cnvnator), str(lumpy), str(delly_deletion), str(delly_insertion), str(delly_inversion), str(delly_duplication), str(genotype), str(atlas), str(stats), str(svviz), str(svviz_only_validated_candidates)])


def main():
    args = parse_arguments()
    
    prefix = args.prefix
    if prefix is None:
        if args.bam.endswith(".bam"):
            prefix = args.bam[:-4]
        else:
            prefix = args.bam[:-5]
    if not args.bam.startswith("/home/dnanexus/in/"):
        args.bam = "/home/dnanexus/in/{0}".format(args.bam)
        args.bai = "/home/dnanexus/in/{0}".format(args.bai)
        args.gatk_jar = "/home/dnanexus/in/{0}".format(args.gatk_jar)
        args.ref_genome = "/home/dnanexus/in/{0}".format(args.ref_genome)

    ref_genome_name = gunzip_input(args.ref_genome)

    run_parliament(args.bam, args.bai, args.gatk_jar, ref_genome_name, prefix, args.filter_short_contigs, args.breakdancer, args.breakseq, args.manta, args.cnvnator, args.lumpy, args.delly_deletion, args.delly_insertion, args.delly_inversion, args.delly_duplication, args.genotype, args.atlas, args.stats, args.svviz, args.svviz_only_validated_candidates)


if __name__ == '__main__':
    main()
