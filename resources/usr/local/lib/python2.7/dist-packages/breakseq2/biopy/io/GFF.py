#!/usr/bin/env python

import sys

class Entry:

	def __init__(self, entry=None):

		if entry is not None and entry.startswith("#"):
			self.is_comment=True
			self.comments=entry
		else:
			self.is_comment=False
			self.comments=None

		fields = entry.rstrip().split("\t") if entry is not None else ["","","","0","0",".",".","."]
		for i in 3,4: fields[i]=int(fields[i])
		self.name, self.source, self.feature, self.start, self.end, self.score, self.strand, self.frame=fields[0:8]
		self.attributes={}
		if len(fields)>8:
			for attr in fields[8].split(";"):
				attr=attr.strip()
				if len(attr)==0: continue
				sp=attr.find(" ")
				attr=(attr[0:sp],attr[sp+1:].strip("\""))
				self.attributes[attr[0]]=attr[-1]

	def __str__(self):
		return "\t".join([self.name, self.source, self.feature, str(self.start), str(self.end), str(self.score), self.strand, str(self.frame)])+"\t"+"; ".join(["%s \"%s\"" % i for i in sorted(self.attributes.items())])
