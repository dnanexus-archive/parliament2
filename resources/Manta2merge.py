import argparse
import os.path
import re

def Convert(fh):
	for line in fh.readlines():
		#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  FHS-CRS-4744.chr20.recaled
		chrom,pos,id,ref,alt,qual,filter,info,format,sample = line.strip().split('\t')
		if "SVTYPE=BND" in line or "SVTYPE=COMPLEX" in line:
                        continue
		pos = int(pos)
		outerstart = "."
		innerstart = "."
		outerend = "."
		innerend = "."
		try:
			end = int(info.split("END=")[1].split(";")[0])
		except:
			print line.strip()
			sys.exit(0)
		starts = [pos]
		ends = [end]
		svtype = alt.split(":")[0].lstrip("<").rstrip(">")
		if "CIPOS" in line:
			outerstart = pos + int(info.split("CIPOS=")[1].split(",")[0]) 
			innerstart = pos + int(info.split("CIPOS=")[1].split(",")[1].split(";")[0])
			if abs(innerstart - outerstart) < 4000:
				starts.append(outerstart)
				starts.append(innerstart)
			else:
				outerstart = "."
				innerstart = "."
		if "CIEND" in line:
			innerend = end + int(info.split("CIEND=")[1].split(",")[0])
			outerend = end + int(info.split("CIEND=")[1].split(",")[1].split(";")[0])
			if abs(innerend - outerend) < 4000:
				ends.append(outerend)
				ends.append(innerend)
			else:
				outerend = "."
				innerend = "."

		if outerstart != ".":
			if outerstart > min(ends):
				outerstart = min(ends) - 1
			if outerstart >= pos:
				outerstart = pos - 1

		if innerstart != ".":
			if innerstart > min(ends):
				innerstart = min(ends) - 1
			if innerstart <= pos:
				innerstart = pos + 1

		if outerend != ".":
			if outerend < max(starts):
				outerend = max(starts) + 1
			if outerend <= end:
				outerend = end + 1

		if innerend != ".":
			if innerend < max(starts):
				innerend = max(starts) + 1
			if innerend >= end:
				innerend = end - 1

		try:
			size = abs(int(info.split("SVLEN=")[1].split(";")[0]))
		except:
			size = 200 
		info = info.replace("IMPRECISE", "PREC=IMPRECISE")
		if(filter == "PASS"):
			if svtype == "DEL":
				if size >= 50:
					fout.write("%s\t%s\t%d\t%s\t%s\t%d\t%s\tDEL\t%d\t%s\n" % (chrom, str(outerstart), min(pos, end), str(innerstart), str(innerend), max(pos, end), str(outerend), abs(size), info))
				if svtype == "DUP":
					if size >= 50:
						fout.write("%s\t%s\t%d\t%s\t%s\t%d\t%s\tINS\t%d\t%s\n" % (chrom, str(outerstart), min(pos, end), str(innerstart), str(innerend), max(pos, end), str(outerend), abs(size), info))
				if svtype == "INS":
                                        if size >= 50:
						fout.write("%s\t%s\t%d\t%s\t%s\t%d\t%s\tINS\t%d\t%s\n" % (chrom, str(outerstart), min(pos, end), str(innerstart), str(innerend), max(pos, end), str(outerend), abs(size), info))
				if svtype == "INV":
					if size >= 50:
						fout.write("%s\t%s\t%d\t%s\t%s\t%d\t%s\tINV\t%d\t%s\n" % (chrom, str(outerstart), min(pos, end), str(innerstart), str(innerend), max(pos, end), str(outerend), abs(size), info))

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
                        help="Manta Version")
        parser.add_argument("input", type=str,\
                        help="Manta final vcf file. Concatenate all the vcf output files into a single vcf")
        parser.add_argument("source", type=str,\
                        help="unique identifier. Fullpath to bam or samplename")
        args = parser.parse_args()
	samplename = os.path.splitext(os.path.basename(args.source))[0]
	svpfile = samplename + "_M.svp"

	fh = open(args.input)
	fout = open(svpfile,'w')
	fout.write("##program=" + args.version+"\n")
	fout.write("##abbrev=M"+"\n")
	fout.write("##source=" + args.source+"\n") 
	pullHeader(fh)
	mergeHeader1 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"
	fout.write(mergeHeader1+"\n")
	Convert(fh)	
fout.close()
