import argparse, math
import re
import os

outputHeader = """##program=CNVnator_v0.2.7
##abbrev=CNV"""

mergeHeader1= """##INFO=<ID="SVPNAME",Number=.,Type=String,Description="unique name given to this event (for uniting with viz info)">
##INFO=<ID="TY",Number=.,Type=Integer,Description="type">
##INFO=<ID="SZ",Number=.,Type=Integer,Description="size">
##INFO=<ID="RD",Number=.,Type=String,Description="normalized read depth - normalized to 1">
##INFO=<ID="P1",Number=.,Type=String,Description="p-value 1 calculated using t-statistic">
##INFO=<ID="P2",Number=.,Type=String,Description="p-value 2 as the probability of RD values within the region to be in the tails of gaussian distribution describing frequencies of RD values in bins.">
##INFO=<ID="P3",Number=.,Type=String,Description="same as p-value 1 but for the middle of the CNV">
##INFO=<ID="P4",Number=.,Type=String,Description="same as p-value 2 but for the middle of the CNV">
##INFO=<ID="Q0",Number=.,Type=String,Description="fraction of reads mapped with q0 quality">"""

mergeHeader2 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str,\
                        help="CNV version")
    parser.add_argument("input", type=str,\
                        help="CNV .calls.txt output file")
    parser.add_argument("source", type=str,\
                        help="unique identifier. Fullpath to bam or samplename")
    args = parser.parse_args()
 
    fh = open(args.input)
    samplename = os.path.splitext(os.path.basename(args.source))[0]
    svpfile = samplename + "_CNV.svp" 
    fout = open(svpfile,'w')
    fout.write("##program=" + args.version+"\n")
    fout.write("##abbrev=CNV"+"\n")
    fout.write("##source=" + args.source+"\n")
    fout.write(mergeHeader1+"\n")
    fout.write(mergeHeader2+"\n")
    
    reduceMap = {".":           "UNK", \
                 "deletion":    "DEL", \
                 "duplication": "INS"}
    
    id = 0
    for line in fh.readlines():
        data = line.strip().split('\t')

        p = float(data[4])
        #filter if p-value is too high
        if p > 0.05:
            continue
        
        #Two filtering extremely large calls
        # 3e+06 and 2e+07...
        chrom,s = data[1].split(':')
        chrom = re.sub('(chr|CHR)',"",chrom)
        start, end = s.split('-')
        
        myType = reduceMap[data[0]]
        try:
            #Note that the new SVP Calls need the size info
            size = int(data[2])
        except ValueError: 
            continue
        if(size >= 100): 
            data.extend([chrom, start, end, id, myType, size])
        
            fout.write(("{9}\t.\t{10}\t.\t.\t{11}\t.\t{13}\t{14}\t"
                   "SVPNAME={12};TY={0};SZ={2};RD={3};P1={4};"
                   "P2={5};P3={6};P4={7};Q0={8}\n").format(*data))
        id += 1
    fout.close()
