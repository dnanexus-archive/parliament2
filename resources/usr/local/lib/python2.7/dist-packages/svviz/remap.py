import collections
import logging
import math
import re
import sys
import time

from svviz.multiprocessor import Multiprocessor

from svviz.utilities import reverseComp, Locus
from svviz.alignment import Alignment, AlignmentSet, AlignmentSetCollection
from svviz.pairfinder import PairFinder
from svviz import misc

def log2(x):
    try:
        return math.log(x, 2)
    except ValueError:
        return float("nan")


def check_swalign():
    try:
        from ssw import ssw_wrap
        aligner = ssw_wrap.Aligner("AGTCGT", report_cigar=True, report_secondary=True)
        aligner.align("AGTC")
    except OSError:
        return False

    return True


class RemapAlignment(object):
    def __init__(self, re_result, query, match):
        self.score = match * len(query)
        self.score2 = None
        self.ref_begin = re_result.start()
        self.ref_end = re_result.end()-1 ### I think this is right
        self.query_begin = 0
        self.query_end = len(query)-1
        self.cigar_string = str(len(query)) + "M"

def tryAlignExact(query, revquery, target, aligner):
    f_results = [m for m in re.finditer(query, target)]
    r_results = [m for m in re.finditer(revquery, target)]

    if len(f_results) > 0:
        aln = RemapAlignment(f_results[0], query, aligner.match)
        strand = "+"
    elif len(r_results) > 0:
        aln = RemapAlignment(r_results[0], revquery, aligner.match)
        strand = "-"
    else:
        return None

    if len(f_results) + len(r_results) > 1:
        aln.score2 = aln.score

    return strand, aln

def alignBothStrands(seq, aligner): #, target):
    revseq = reverseComp(seq)

    forward_al = aligner.align(seq)
    reverse_al = aligner.align(revseq)

    strand = None

    if not forward_al:
        if reverse_al:
            strand = "-"
    else:
        if not reverse_al:
            strand = "+"
        else:
            if forward_al.score >= reverse_al.score:
                strand = "+"
                if reverse_al.score > forward_al.score2:
                    forward_al.score2 = reverse_al.score
                    forward_al.ref_end2 = -1
            else:
                strand = "-"
                if forward_al.score > reverse_al.score2:
                    reverse_al.score2 = forward_al.score
                    reverse_al.ref_end2 = -1

    if strand == "+":
        return "+", forward_al
    else:
        return "-", reverse_al



class Multimap(Multiprocessor):
    def __init__(self, namesToReferences, tryExact=False):
        from ssw import ssw_wrap

        self.tryExact = tryExact

        self.namesToAligners = {}
        self.namesToRefs = {}

        for name, ref in namesToReferences.items():
            self.namesToAligners[name] = ssw_wrap.Aligner(ref, report_cigar=True, report_secondary=True)
            self.namesToRefs[name] = ref

    def remap(self, seq):
        results = {}
        for name, aligner in self.namesToAligners.items():
            results[name] = None

            if self.tryExact:
                revseq = reverseComp(seq)
                results[name] = tryAlignExact(seq, revseq, self.namesToRefs[name], aligner)

            if results[name] is None:
                results[name] = alignBothStrands(seq, aligner)#, self.namesToRefs[name])

        return seq, results


def filterDegenerateOnly(reads):
    degenerateOnly = set("N")
    filtered = [read for read in reads if set(read.seq) != degenerateOnly]
    if len(filtered) < len(reads):
        logging.info("  Removed {} reads with only degenerate nucleotides ('N')".format(len(reads)-len(filtered)))
    return filtered

def chooseBestAlignment(read, mappings, chromPartsCollection):
    # TODO: this should be read-pair aware
    # TODO: this is kind of ridiculous; we need to make pickleable reads that can be sent to 
    # and from the Multimapper
    # mappings: name -> (strand, aln)
    bestName = None
    bestAln = None
    bestStrand = None
    secondScore = None

    for name, mapping in mappings.items():
        if mapping is None:
            return None
        strand, aln = mapping
        if bestAln is None or aln.score > bestAln.score:
            bestName = name
            bestAln = aln
            bestStrand = strand

    for name, mapping in mappings.items():
        strand, aln = mapping
        if name == bestName:
            if secondScore is None or bestAln.score2 > secondScore:
                secondScore = bestAln.score2
        else:
            if secondScore is None or aln.score > secondScore:
                secondScore = aln.score

    seq = read.seq
    genome_seq = chromPartsCollection.getPart(bestName).getSeq()[bestAln.ref_begin:bestAln.ref_end+1].upper()

    if bestStrand == "-":
        seq = reverseComp(seq)
    if read.is_reverse:
        bestStrand = "+" if bestStrand=="-" else "-"
    bestAln = Alignment(read.qname, bestName, bestAln.ref_begin, bestAln.ref_end, bestStrand, seq, bestAln.cigar_string, 
                    bestAln.score, genome_seq, secondScore, read.mapq)
    return bestAln


def do1remap(chromPartsCollection, reads, processes, jobName="", tryExact=False):
    reads = filterDegenerateOnly(reads)

    namesToReferences = {}
    for name, chromPart in chromPartsCollection.parts.items():
        namesToReferences[chromPart.id] = chromPart.getSeq()

    # map each read sequence against each chromosome part (the current allele only)

    if processes == -1:
        from svviz import alignproc
        logging.info(" == aligning using slower subprocesses for error-prone "
            "datasets (eg pacbio) ==")
        remapped = alignproc.multimap(namesToReferences, [read.seq for read in reads])
        # raise Exception("not yet implemented")
    elif processes != 1:
        verbose = 3

        remapped = dict(Multimap.map(Multimap.remap, [read.seq for read in reads], initArgs=[namesToReferences], 
            verbose=verbose, processes=processes, name=jobName))
    else:
        mapper = Multimap(namesToReferences, tryExact=tryExact)

        remapped = {}
        for i, read in enumerate(reads):
            if i % 1000 == 0:
                logging.debug("realigned {} of {} reads".format(i, len(reads)))
            seq, result = mapper.remap(read.seq)
            remapped[seq] = result

    alignmentSets = collections.defaultdict(AlignmentSet)
    badReads = set()

    for read in reads:
        # TODO: for paired-end, if there are equally-scoring alignments in multiple parts, we should pick
        # the pair which are in the correct orientation
        aln = chooseBestAlignment(read, remapped[read.seq], chromPartsCollection)
        if aln is None:
            badReads.add(read.qname)
        else:
            alignmentSets[read.qname].addAlignment(aln)

    return alignmentSets, badReads



def do_realign(dataHub, sample):
    processes = dataHub.args.processes
    if processes is None or processes == 0:
        # we don't really gain from using virtual cores, so try to figure out how many physical
        # cores we have
        processes = misc.cpu_count_physical()

    variant = dataHub.variant
    reads = sample.reads
    name = "{}:{{}}".format(sample.name[:15])

    t0 = time.time()
    refalignments, badReadsRef = do1remap(variant.chromParts("ref"), reads, processes, 
        jobName=name.format("ref"), tryExact=dataHub.args.fast)
    altalignments, badReadsAlt = do1remap(variant.chromParts("alt"), reads, processes, 
        jobName=name.format("alt"), tryExact=dataHub.args.fast)
    t1 = time.time()

    logging.debug(" Time to realign: {:.1f}s".format(t1-t0))

    badReads = badReadsRef.union(badReadsAlt)

    if len(badReads) > 0:
        logging.warn(" Alignment failed with {} reads (this is a known issue)".format(badReads))
        for badRead in badReads:
            refalignments.pop(badRead, None)
            altalignments.pop(badRead, None)

    assert set(refalignments.keys()) == set(altalignments.keys()), \
                    set(refalignments.keys()) ^ set(altalignments.keys())

    alnCollections = []
    for key in refalignments:
        alnCollection = AlignmentSetCollection(key)
        alnCollection.addSet(refalignments[key], "ref")
        alnCollection.addSet(altalignments[key], "alt")
        alnCollections.append(alnCollection)

    return alnCollections



def _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, include_supplementary, max_reads, sample_reads):
    pairFinder = PairFinder(searchRegions, bam, minmapq=minmapq, pair_minmapq=pair_minmapq,
        is_paired=(not single_ended), include_supplementary=include_supplementary, max_reads=max_reads, sample_reads=sample_reads)
    reads = [item for sublist in pairFinder.matched for item in sublist]
    return reads, pairFinder.supplementaryAlignmentsFound

def getReads(variant, bam, minmapq, pair_minmapq, searchDistance, single_ended=False, include_supplementary=False, max_reads=None, sample_reads=None):
    t0 = time.time()
    searchRegions = variant.searchRegions(searchDistance)

    # This cludge tries the chromosomes as given ('chr4' or '4') and if that doesn't work
    # tries to switch to the other variation ('4' or 'chr4')
    try:
        reads, supplementaryAlignmentsFound = _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, 
            include_supplementary, max_reads, sample_reads)
    except ValueError as e:
        oldchrom = searchRegions[0].chr()
        try:
            if "chr" in oldchrom:
                newchrom = oldchrom.replace("chr", "")
                searchRegions = [Locus(l.chr().replace("chr", ""), l.start(), l.end(), l.strand()) for l in searchRegions]
            else:
                newchrom = "chr{}".format(oldchrom)
                searchRegions = [Locus("chr{}".format(l.chr()), l.start(), l.end(), l.strand()) for l in searchRegions]

            logging.warn("  Couldn't find reads on chromosome '{}'; trying instead '{}'".format(oldchrom, newchrom))

            reads, supplementaryAlignmentsFound = _getreads(searchRegions, bam, minmapq, pair_minmapq, single_ended, 
                include_supplementary, max_reads, sample_reads)

        except ValueError:
            raise e
    t1 = time.time()

    if supplementaryAlignmentsFound:
        logging.warn("  ** Supplementary alignments found: these alignments (with sam flag 0x800) **\n"
                     "  ** are poorly documented among mapping software and may result in missing **\n"
                     "  ** portions of reads; consider using the --include-supplementary          **\n"
                     "  ** command line argument if you think this is happening                   **")
        
    logging.debug("  time to find reads and mates:{:.1f}s".format(t1 - t0))
    logging.info("  number of reads found: {}".format(len(reads)))

    return reads


def main():
    pass
    # genomeFastaPath = sys.argv[1]
    # genome = pyfaidx.Fasta(genomeFastaPath, as_raw=True)

    # bamPath = sys.argv[2]
    # bam = pysam.Samfile(bamPath, "rb")

    # eventType = sys.argv[3]

    # if eventType.lower().startswith("del"):
    #     if len(sys.argv) == 4:
    #         chrom, start, end = "chr1", 72766323, 72811840
    #     else:
    #         chrom = sys.argv[4]
    #         start = int(sys.argv[5])
    #         end = int(sys.argv[6])
    #     minmapq = 30

    #     variant = StructuralVariants.Deletion.from_breakpoints(chrom, start-1, end-1, extraSpace, genome)

    # elif eventType.lower().startswith("ins"):
    #     if len(sys.argv) == 4:
    #         chrom, pos, seq = "chr3", 20090540, L1SEQ
    #     else:
    #         chrom = sys.argv[4]
    #         pos = int(sys.argv[5])
    #         seq = int(sys.argv[6])
    #     minmapq = -1
    #     variant = StructuralVariants.Insertion(Locus(chrom, pos, pos, "+"), reverseComp(seq), extraSpace, genome)





if __name__ == '__main__':
    main()
