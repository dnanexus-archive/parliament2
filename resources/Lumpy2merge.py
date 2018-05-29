import argparse
import os.path
import re
import sys
import math 

def Convert(fh):
	for line in fh.readlines():
		if line[0] == "#":
			continue
		fields = line.strip().split('\t')
		chr1,outS,inS,chr2,inE,outE,x,y,u,v,svtype,info = line.strip().split('\t')[0:12]
		info = info.split(":")[0]
		if outS < 1:
                        outS = 1
		outS = int(outS)
		outE = int(outE)
		inS = int(inS)
		inE = int(inE)
		start = (outS + inS)/2
		end = (outE+inE)/2
		size = abs(end - start)
		if svtype == "DUP":
			svtype = "DUPLICATION"
		if svtype == "DEL":
			svtype = "DELETION"
		if svtype == "INV":
			svtype = "INVERSION"
		if svtype == "BND":
			svtype = "INTERCHROM"


		if svtype == "INTERCHROM":
			size1 = outE - start
			size2 = outS - end
			fout.write("%s\t.\t%d\t.\t.\t.\t%d\tMIS\t%d\tPREC=%s\n" %(chr1, \
											start, \
											outE, \
											abs(size1), \
											info)) 
			fout.write("%s\t%d\t.\t.\t.\t%d\t.\tMIS\t%d\tPREC=%s\n" %(chr2, \
											outS, \
											end, \
											abs(size2), \
											info))
		else:
			if svtype == "DELETION":
				if size >= 100:
				#if size > 0:
					fout.write("%s\t.\t%d\t.\t.\t%d\t.\tDEL\t%d\tPREC=%s\n" % (chr1, \
													  start,\
													  end, \
													  abs(size), \
													  info))
			if svtype == "DUPLICATION":
				if size >= 100:
					fout.write("%s\t.\t%d\t.\t.\t%d\t.\tINS\t%d\tPREC=%s\n" % (chr1, \
													   start,\
													   end, \
													   abs(size), \
													   info))
			if svtype == "INVERSION":
				if size >= 300:
					fout.write("%s\t.\t%d\t.\t.\t%d\t.\tMIS\t%d\tPREC=%s\n" % (chr1, \
                                                	                                                 start, \
                                                        	                                         end, \
                                                                        	                         abs(size), \
                                                                                	                 info))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
        parser.add_argument("input", type=str,\
                        help="Lumpy final file")
	parser.add_argument("svp", type=str,\
                        help="outputfile")
	parser.add_argument("source", type=str,\
                        help="samplename")
        args = parser.parse_args()
	fh = open(args.input)
	samplename = args.source
        svpfile = args.svp + "_L.svp"
	fout = open(svpfile,'w')
	fout.write("##program=Lumpy\n")
	fout.write("##abbrev=L"+"\n")
	fout.write("##source="+samplename+"\n") 
	mergeHeader1 = """##INFO=<ID=PREC,Number=0,Type=Flag,Description="Imprecise or Precise structural variation">"""
	mergeHeader2 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"
	fout.write(mergeHeader1+"\n")
	fout.write(mergeHeader2+"\n")
	Convert(fh)	
