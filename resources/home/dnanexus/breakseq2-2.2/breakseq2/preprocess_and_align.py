#!/usr/bin/env python

import argparse
import os
import time
import subprocess
from functools import partial
from breakseq_pre import print_candidate_reads
import logging
import multiprocessing
import traceback
import shutil


def add_options(main_parser):
    local_parser = main_parser.add_argument_group("Read alignment options")
    local_parser.add_argument("--bplib", help="Breakpoint library FASTA", required=False)
    local_parser.add_argument("--bwa", help="Path to BWA executable", required=True)
    local_parser.add_argument("--samtools", help="Path to SAMtools executable", required=True)


def preprocess_and_align(bplib=None, bwa=None, samtools=None, bam=None, prefix=None, chromosome=None, keep_temp=False):
    func_logger = logging.getLogger("%s-%s" % (preprocess_and_align.__name__, multiprocessing.current_process()))
    outfq = prefix + ".fq"
    # First generate the FASTQ for alignment
    outbam = None
    try:
        func_logger.info("Extracting candidate reads from {bam} for chromosome {chromosome} and aligning against {bplib}".format(bam=bam, chromosome=chromosome, bplib=bplib))
        readcount = print_candidate_reads([bam], chromosome, outfile=outfq)
        if readcount > 0:
            outbam = prefix + ".bam"
            outlog = prefix + ".bwa.log"
            bash_cmd = "bash -c \"{bwa} samse {bplib} <({bwa} aln {bplib} {outfq}) {outfq} | {samtools} view -S - -1 -F 4 -bo {outbam}\"".format(bwa=bwa, bplib=bplib, samtools=samtools, outfq=outfq, outbam=outbam)
            func_logger.info("Running %s" % bash_cmd)
            with open(outlog, "w") as logfd:
                start_time = time.time()
                subprocess.check_call(bash_cmd, shell=True, stderr=logfd)
                func_logger.info("Finished %s (%g s)" % (bash_cmd, time.time() - start_time))
        else:
            func_logger.info("No reads extracted from {bam} so no alignment will be done".format(bam=bam))
    except Exception as e:
        func_logger.error('Caught exception in worker thread')
        traceback.print_exc()

        print()
        raise e

    if not keep_temp:
        os.remove(outfq)
    return outbam


def preprocess_and_align_callback(result, result_list):
    if result is not None:
        result_list.append(result)


# Parallelize over BAMs and chromosomes
def parallel_preprocess_and_align(bplib, bwa, samtools, bams, work, chromosomes=[], nthreads=1, keep_temp=False):
    func_logger = logging.getLogger(parallel_preprocess_and_align.__name__)
    start_time = time.time()

    if not os.path.isdir(work):
        os.makedirs(work)

    if not chromosomes: chromosomes = [None]
    else: chromosomes.append("") # Special contig for unmapped reads

    pool = multiprocessing.Pool(nthreads)
    count = 0
    aligned_bams = []
    for bam  in bams:
        for chromosome in chromosomes:
            kwargs_dict = {"bplib": bplib, "bwa": bwa, "samtools": samtools, "bam": bam, "prefix": "%s/%d" % (work, count), "chromosome": chromosome, "keep_temp": keep_temp}
            pool.apply_async(preprocess_and_align, args=[], kwds=kwargs_dict, callback=partial(preprocess_and_align_callback, result_list=aligned_bams))
            count += 1

    pool.close()
    pool.join()

    # Now merge the BAMs together
    if not aligned_bams:
        func_logger.info("No alignment generated after read extraction")
        return []

    finalbam = os.path.join(work, "final.bam")
    if len(aligned_bams) > 1:
        merged_str = " ".join(aligned_bams)
        bash_cmd = "bash -c \"{samtools} merge -f {finalbam} {merged_str}\"".format(samtools=samtools, finalbam=finalbam, merged_str=merged_str)
        subprocess.check_call(bash_cmd, shell=True)
    else:
        shutil.copy(aligned_bams[0], finalbam)

    if not keep_temp:
        for bam in aligned_bams:
            os.remove(bam)

    func_logger.info("Finished parallel preprocess and align (%g s)." % (time.time() - start_time))
    return [finalbam]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process BAMs to generate candidate reads and align them against the breakpoint library")
    add_options(parser)
    parser.add_argument("--bams", nargs="+", help="BAMs to extract reads from", required=True)
    parser.add_argument("--chromosomes", nargs="+", help="List of chromosomes to process", default=[])
    parser.add_argument("--work", help="Working directory")
    parser.add_argument("--nthreads", help="Number of processes to use", type=int, default=1)
    parser.add_argument("--keep_temp", help="Keep temporary files", action="store_true")

    args = parser.parse_args()
    preprocess_and_align(args.bplib, args.bwa, args.samtools, args.bams, args.chromosomes, args.nthreads, args.keep_temp)
