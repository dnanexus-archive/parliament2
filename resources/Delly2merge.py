import argparse
import os.path
import os
import re
import sys

def Convert(fh):
	for line in fh.readlines():
		try:
			chrom,pos,id,ref,alt,qual,filter,info,format,sample = line.strip().split('\t')
			pos = int(pos)
			# IMPRECISE;CIEND=-210,210;CIPOS=-210,210;SVTYPE=TRA;SVMETHOD=EMBL.DELLY;CHR2=4;END=190202827;SVLEN=0;CT=3to3;PE=5;MAPQ=0
			# PRECISE;CIEND=-10,10;CIPOS=-10,10;SVTYPE=DEL;SVMETHOD=EMBL.DELLYv0.7.2;CHR2=chr1;END=88946;CT=3to5;INSLEN=0;PE=0;MAPQ=23;SR=3;SRQ=1;CONSENSUS=
			svtype = info.split("SVTYPE=")[1].split(";")[0]
			chrom2 = info.split("CHR2=")[1].split(";")[0]
			end = int(info.split(";END=")[1].split(";")[0])
			pe = int(info.split(";PE=")[1].split(";")[0])
			mapq = int(info.split("MAPQ=")[1].split(";")[0])
			if(pe >= 6 and mapq >= 20):
				if svtype == "TRA":
					start = pos
					outerEnd = pos + 200
					outerStart = end - 200
					size = 200
					fout.write("%s\t.\t%d\t.\t.\t.\t%d\tMIS\t%d\tPREC=%s\n" %(chrom, \
												  pos, \
												  outerEnd, \
													  abs(size), \
													  info)) 
					fout.write("%s\t%d\t.\t.\t.\t%d\t.\tMIS\t%d\tPREC=%s\n" %(chrom2, \
													  outerStart, \
													  end, \
													  abs(size), \
													  info)) 
				elif svtype == "DEL":
					size = abs(end - pos)
					if size >= 300:
						fout.write("%s\t.\t%d\t.\t.\t%d\t.\tDEL\t%d\tPREC=%s\n" % (chrom, \
														   pos,\
														   end, \
														   abs(size), \
														   info))
				elif svtype == "DUP":
					size = abs(end - pos)
					if size >= 300:
						fout.write("%s\t.\t%d\t.\t.\t%d\t.\tINS\t%d\tPREC=%s\n" % (chrom, \
														   pos,\
														   end, \
														   abs(size), \
														   info))
				elif svtype == "INV":
					size = abs(end - pos)
					if size >= 300:
						fout.write("%s\t.\t%d\t.\t.\t%d\t.\tMIS\t%d\tPREC=%s\n" % (chrom, \
														   pos, \
														   end, \
														   abs(size), \
														   info))
				elif svtype == "INS":
                                        size = int(info.split("INSLEN=")[1].split("\t")[0])
                                        if size >= 50:
                                                fout.write("%s\t.\t%d\t.\t.\t%d\t.\tMIS\t%d\tPREC=%s\n" % (chrom, \
                                                                                                                   pos, \
                                                                                                                   end, \
                                                                                                                   abs(size), \
                                                                                                                   info))
		except:
			sys.stderr.write(line)
			pass

def pullHeader(fh):
    """
    Pulls the header from vcf file
    """
    while True:
        line = fh.readline()
        if line.startswith("##INFO=<ID=IMPRECISE"):
	    continue
	if line.startswith("##INFO=<ID=PRECISE"):
	    continue
	if line.startswith("##INFO="):	
            #sys.stdout.write(line)
            fout.write(line)
        if line.startswith("##FOR"):
            #sys.stdout.write(line.replace("FORMAT","INFO"))
            fout.write(line.replace("FORMAT","INFO"))           
        if line.startswith("#CH"):
            return

        if line is None:
            sys.stderr.write("ERROR! No read good.\n")
            exit(10)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
        parser.add_argument("version", type=str,\
                        help="Delly version")
        parser.add_argument("input", type=str,\
                        help="Delly final vcf file. Concatenate all the vcf output files into a single vcf")
        parser.add_argument("source", type=str,\
                        help="unique identifier. Fullpath to bam or samplename")
        args = parser.parse_args()
	samplename = os.path.splitext(os.path.basename(args.source))[0]
	svpfile = samplename + "_D.svp"

	if os.stat(args.input).st_size == 0:
		sys.stderr.write("%s is empty\n" % args.input)
		sys.exit(1)
	fh = open(args.input)
	fout = open(svpfile,'w')
	fout.write("##program=" + args.version+"\n")
	fout.write("##abbrev=D"+"\n")
	fout.write("##source=" + args.source+"\n") 
	pullHeader(fh)
	mergeHeader1 = """##INFO=<ID=PREC,Number=0,Type=Flag,Description="Imprecise or Precise structural variation">"""
	mergeHeader2 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"
	fout.write(mergeHeader1+"\n")
	fout.write(mergeHeader2+"\n")
	Convert(fh)	
fout.close()
