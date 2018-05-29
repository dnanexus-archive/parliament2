#!/bin/en python
import os
from Bio import SeqIO

class Seqs:

	def __init__(self, base, window=0):
		self.base=base
		self.window=window
		self.half_window=window/2
		self.seqs={}

	def get_sequence(self, name, start=None, end=None):
		if name not in self.seqs:
			if os.path.isdir(self.base):
				self.seqs[name] = parse(self.base+"/"+name+".fa").next()
			else:
				self.seqs = parse(self.base, todict=True)
		if end is None: end=start
		seq = self.seqs[name].seq
		return str(seq if start is None else seq[(start-1):min(end,len(seq))])

	def get_window(self, name, start, end=None, window=None):
		if end is None: end=start
		hw = self.half_window if window is None else window/2
		ws = start - hw
		we = end + hw - (1 if start==end and hw>0 else 0)
		return (name, ws, we)

def parse(file, todict=False):
	handle = open(file, "rU")
	seqs   = SeqIO.parse(handle, "fasta")
	return seqs if not todict else SeqIO.to_dict(seqs)

coms={"A":"T","T":"A","C":"G","G":"C","U":"A","N":"N","a":"t","t":"a","c":"g","g":"c","u":"a","n":"n"}

def complement(seq, rna=False):
	i=""
	for n in range(len(seq)-1, -1, -1):
		c=coms[seq[n]]
		if rna: c=c.replace("T","U").replace("t","u")
		i=i+c
	return i

