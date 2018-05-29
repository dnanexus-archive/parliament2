#!/usr/bin/env python

import logging
import os
import time
import subprocess
import shutil
import pysam
import preprocess_and_align
import breakseq_core
import breakseq_post
import compute_zygosity
import gen_vcf
import breakseq_index
from _version import __version__


def add_options(main_parser):
    preprocess_and_align.add_options(main_parser)
    breakseq_core.add_options(main_parser)
    breakseq_post.add_options(main_parser)
    compute_zygosity.add_options(main_parser)
    gen_vcf.add_options(main_parser)
    breakseq_index.add_options(main_parser)

    main_parser.add_argument("--nthreads", help="Number of processes to use for parallelism", type=int, default=1)
    main_parser.add_argument("--bams", help="Alignment BAMs", nargs="+", required=True, default=[])
    main_parser.add_argument("--work", help="Working directory", default="work")
    main_parser.add_argument("--chromosomes", nargs="+", help="List of chromosomes to process", default=[])
    main_parser.add_argument("--reference", help="Reference FASTA", required=True)
    main_parser.add_argument("--sample", help="Sample name. Leave unspecified to infer sample name from BAMs.")
    main_parser.add_argument("--keep_temp", help="Keep temporary files", action="store_true")
    main_parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)


def infer_sample(bam):
    samfile = pysam.Samfile(bam, "rb")
    if "RG" not in samfile.header:
        raise Exception("Unable to infer sample name from %s since RG is missing" % bam)
    samples = list(set([item["SM"] for item in samfile.header["RG"]]))
    if len(samples) > 1:
        raise Exception("Multiple samples found: %s" % (", ".join(samples)))
    samfile.close()
    return samples[0]

def has_bwa_index(fasta):
    for suffix in ["amb", "ann", "bwt", "pac", "sa"]:
        if not os.path.isfile("%s.%s" % (fasta, suffix)):
            return False
    return True


def get_reference_contigs(reference):
    func_logger = logging.getLogger(get_reference_contigs.__name__)
    fai = "%s.fai" % reference
    func_logger.info("Extracting chromosome names from %s" % fai)
    with open(fai) as fai_fd:
        contigs = [line.split()[0] for line in fai_fd]
    return contigs


def breakseq2_workflow(sample=None, bplib=None, bplib_gff=None, bwa=None, samtools=None, bams=[], work="work", chromosomes=[],
                       nthreads=1, min_span=breakseq_core.DEFAULT_MIN_SPAN,
                       min_overlap=compute_zygosity.DEFAULT_MIN_OVERLAP, reference=None, keep_temp=False, window=compute_zygosity.DEFAULT_WINDOW, junction_length=breakseq_index.DEFAULT_JUNCTION_LENGTH):
    func_logger = logging.getLogger(breakseq2_workflow.__name__)

    start_time = time.time()
    bams = [os.path.abspath(bam) for bam in bams]

    if not bams:
        func_logger.error("No BAMs specified so nothing to do")
        return os.EX_NOINPUT

    if not sample:
        sample = infer_sample(bams[0])

    if not os.path.isdir(work):
        func_logger.info("Created working directory %s" % work)
        os.makedirs(work)

    if not bplib and not bplib_gff:
        func_logger.error("Atleast one of the breakpoint FASTA or GFF must be specified")
        return os.EX_USAGE

    for fname in [bplib, bplib_gff]:
        if fname is None: continue
        if not os.path.isfile(fname):
            raise Exception("Breakpoint library %s not a file" % fname)
        if os.path.getsize(fname) == 0:
            raise Exception("Breakpoint library %s empty" % fname)

    if bplib_gff:
        # Generate bplib using the GFF file and use this for the main run
        bplib = os.path.join(work, "bplib.fa")
        func_logger.info("Generating breakpoint-library using %s" % bplib_gff)
        breakseq_index.generate_bplib(bplib_gff, reference, bplib, junction_length)
    elif not has_bwa_index(bplib):
        new_bplib = os.path.join(work, "bplib.fa")
        func_logger.info("Index of %s does not exist. Copying to %s to index" % (bplib, work))
        if os.path.realpath(new_bplib) != os.path.realpath(bplib):
            shutil.copyfile(bplib, new_bplib)
        bplib = new_bplib

    if not has_bwa_index(bplib):
        # Index the bplib
        index_cmd = "{bwa} index {bplib}".format(bwa=bwa, bplib=bplib)
        func_logger.info("Indexing {bplib} using {index_cmd}".format(bplib=bplib, index_cmd=index_cmd))
        with open(os.path.join(work, "index.log"), "w") as index_log_fd:
            subprocess.check_call(index_cmd, shell=True, stderr=index_log_fd)

    if not chromosomes:
        chromosomes = get_reference_contigs(reference)

    aligned_bams = preprocess_and_align.parallel_preprocess_and_align(bplib, bwa, samtools, bams, work, chromosomes,
                                                                      nthreads, keep_temp)

    if not aligned_bams:
        func_logger.warn("Read-extraction and alignment generated nothing")
        return os.EX_OK

    breakseq_core.breakseq_core(aligned_bams, "%s/breakseq.out" % work, min_span=min_span, chromosomes=chromosomes)
    breakseq_post.generate_final_gff(["%s/breakseq.out" % work], "%s/breakseq.gff" % work)
    compute_zygosity.compute_zygosity(bams, window, "%s/breakseq.gff" % work, "%s/breakseq_genotyped.gff" % work,
                                      min_overlap)
    gen_vcf.gff_to_vcf(reference, "%s/breakseq_genotyped.gff" % work, sample, "%s/breakseq.vcf" % work)

    func_logger.info("Done! (%g s)" % (time.time() - start_time))

    return os.EX_OK
