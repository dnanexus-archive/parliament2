from ssw import ssw_wrap
from svviz import remap

def align(ref, seq):
	aligner = ssw_wrap.Aligner(ref, report_cigar=True, report_secondary=True)
	result = remap.alignBothStrands(seq, aligner)
	print result
	
if __name__ == '__main__':
	import sys
	ref = sys.argv[0]
	seq = sys.argv[1]
