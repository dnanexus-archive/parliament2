#!/usr/bin/env python

import sys, os, logging
import Fasta
import GFF

class Call(GFF.Entry):

	def __init__(self, entry=None, inserted=None, base=None):
		GFF.Entry.__init__(self, entry)
		self.inserted=inserted
		self.base=base
		if "Id" in self.attributes:
			self.id=self.attributes["Id"]
		else:
			self.id="%s:%s-%s:%s:%s"%(self.name, self.start, self.end, self.source, self.event())

	def size(self):
		if self.is_insertion():
			return len(self.get_sequence())
		else:
			return abs(self.end-self.start)+1

	def event(self, event=None, flip=False):
		if flip:
			event=self.event_flipped()
		if event is None: return self.feature
		else: self.feature=event

	def event_flipped(self):
		if self.is_insertion(): return "Deletion"
		elif self.is_deletion(): return "Insertion"
		else: return event

	def mech(self, mech=None):
		if mech is None: return self.attributes["Mech"]
		else: self.attributes["Mech"]=mech

	def rect(self, status=None):
		if status is None: return (None if "Rect" not in self.attributes else self.attributes["Rect"])
		else: self.attributes["Rect"]=status

	def rect_status(self, unique=False):
		rs = []
		r = self.rectified()
		if r is not None: rs = [int(s) for s in r.split(":")]
		return rs if not unique else set(rs)

	def ancestral_state(self, state=None):
		if state is not None:
			self.attributes["AncestralState"]=state
		return self.attributes["AncestralState"] if "AncestralState" in self.attributes else None

	def is_rectified(self):
		for s in self.rectified_status():
			if s != 0: return s
		return 0
	
	def is_rectifiable(self):
		c = 0
		for s in self.rectified_status():
			if s != 0: c+=1
		return c

	def is_consistently_rectifiable(self):
		r = 0
		c = 0
		for s in self.rectified_status():
			if s !=0: 
				if r==0: r=s
				if r!=s: return 0
				c+=1
		return c

	def trace(self, origin=None):
		if origin is None: return (None if "Trace" not in self.attributes else self.attributes["Trace"])
		else: self.attributes["Trace"]=origin

	def is_intra(self):
		t=self.trace()
		return t is not None and t.lower().find("intra")>-1

	def is_inter(self):
                t=self.trace()
                return t is not None and t.lower().find("inter")>-1

	def is_insertion(self):
		return self.event().lower()=="insertion"

	def is_deletion(self):
		return self.event().lower()=="deletion"

	def is_inversion(self):
		return self.event().lower()=="inversion"

	def is_indel(self):
		return self.is_insertion() or self.is_deletion()

	def get_sequence(self):
		if self.is_insertion() and self.inserted is not None:
			return self.inserted
		else:
			return self.base.get_sequence(self.name, self.start, self.end)

	def get_flanks(self):
		seqA, seqB, seqC = None, None, None
		if self.base is not None:
			seqs=self.base
			if self.end == 0:
				seqA=seqs.get_sequence(*seqs.get_window(self.name, self.start))
			else:
				if self.is_insertion():
					seqC1=seqs.get_sequence(self.name, self.start-seqs.half_window+1, self.start)
					seqC2=seqs.get_sequence(self.name, self.end, self.end+seqs.half_window-1)
					if self.inserted is not None:
						seqA=seqC1+self.inserted[0:seqs.half_window]
						seqB=self.inserted[-seqs.half_window:]+seqC2
					seqC=seqC1+seqC2
				else:
					seqA=seqs.get_sequence(*seqs.get_window(self.name, self.start))
					seqB=seqs.get_sequence(*seqs.get_window(self.name, self.end+1))
					seqC=seqA[0:seqs.half_window]+seqB[seqs.half_window:]
		return seqA, seqB, seqC


def parse(gff_file, base=None):
	logger = logging.getLogger(parse.__name__)

	ins_file=gff_file.replace(".gff","")+".ins"
	insertions=None if not os.path.exists(ins_file) else Fasta.parse(ins_file, todict=True)
	if insertions is None:
		logger.warn("Insertion sequence file %s missing" % ins_file)

	calls=[]
	for entry in open(gff_file, "r"):
		if entry.startswith("#"): continue
		try:
			call=Call(entry, base=base)
			if insertions is not None and call.id in insertions: call.inserted=str(insertions[call.id].seq)
			elif "Iseq" in call.attributes: 
				call.inserted=call.attributes["Iseq"]
				del call.attributes["Iseq"]
			calls.append(call)
		except:
			logger.error("Unable to parse line: %s" % entry)
			raise
	return calls

def hash(calls):
	hash={}
	for call in calls:
		hash[call.id]=call
	return hash

def cluster(calls, bymech=True):
	hash={}
	for call in calls:
		key = call.mech() if bymech else call.event()
		if key not in hash:
			hash[key]=[]
		hash[key].append(call)
	return hash
