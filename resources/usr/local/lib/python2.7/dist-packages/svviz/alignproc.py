"""
this module wraps the ssw_wrap Smith-Waterman alignment code in a subprocess
because ssw can occasionally segfault when aligning long reads against a reasonably
large reference sequence; when the subprocess segfaults, this is detected below
and the result is skipped

not yet implemented: try aligning the reverse complement when the original sequence
causes a segfault, then reverse the strand
"""
from __future__ import print_function

import collections
import multiprocessing
import os
import six
import subprocess

from svviz import misc
from ssw import ssw_wrap
from svviz import remap


Aln = collections.namedtuple("Aln", ["ref_begin", "ref_end", "cigar_string", "score", "score2"])



def alignProcWrapper(ref, seq):
    cmd = "python {} {} {}".format(
        os.path.realpath(__file__),
        ref,
        seq)
    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if proc.returncode != 0:
        return None

    fields = out.split()
    strand = fields[0].decode()
    
    aln = Aln(int(fields[1]), int(fields[2]), fields[3].decode(), int(fields[4]), int(fields[5]))

    return strand, aln

def remaps(args):
    namesToReferences, seq = args
    seqresult = {}
    for name, ref in namesToReferences.items():
        seqresult[name] = alignProcWrapper(ref, seq)
    return seq, seqresult

def multimap(namesToReferences, seqs):
    if not hasattr(multimap, "pool"):
        multimap.pool = multiprocessing.Pool(processes=misc.cpu_count_physical())

    pool = multimap.pool

    results = {}
    results = dict(pool.map_async(remaps, [(namesToReferences, seq) for seq in seqs]).get(999999))
    # results = dict(map(remaps, [(namesToReferences, seq) for seq in seqs]))

    return results

def align(ref, seq):
    aligner = ssw_wrap.Aligner(ref, report_cigar=True, report_secondary=True)
    strand, aln = remap.alignBothStrands(seq, aligner)
    
    print(strand, aln.ref_begin, aln.ref_end, aln.cigar_string, aln.score, aln.score2)
    

if __name__ == '__main__':
    import sys
    ref = sys.argv[1]
    seq = sys.argv[2]

    align(ref, seq)
