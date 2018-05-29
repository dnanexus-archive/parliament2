import argparse
import os.path
import re

def Convert(fh):
    for line in fh.readlines():
        #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  FHS-CRS-4744.chr20.recaled
        chrom,pos,locus_id,ref,alt,qual,fil,info,formt,sample = line.strip().split('\t')
        pos = int(pos)
        # 1       46366107        .       T       <DEL>   .       PASS    SVLEN=-329;SVTYPE=DEL;END=46366436      GT:ABC:PE:REFCOUNTS     0/1:0,0,6:6:17,8
        svtype = alt.split(":")[0].lstrip("<").rstrip(">")
        end = int(info.split("END=")[1].split(";")[0])
        size = abs(int(info.split("SVLEN=")[1].split(";")[0]))
        if(fil == "PASS"):
            if svtype == "DEL":
                if size >= 100:
                    fout.write("%s\t.\t%d\t.\t.\t%d\t.\tDEL\t%d\t%s\n" % (chrom, min(pos, end),max(pos, end), abs(size), info))
                if svtype == "DUP":
                    if size >= 100:
                        fout.write("%s\t.\t%d\t.\t.\t%d\t.\tINS\t%d\t%s\n" % (chrom, min(pos, end),max(pos, end), abs(size), info))
                if svtype == "INV":
                    if size >= 100:
                        fout.write("%s\t.\t%d\t.\t.\t%d\t.\tINV\t%d\t%s\n" % (chrom, min(pos, end),max(pos, end), abs(size), info))
        

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
    parser.add_argument("version", type=str, help="Breakseq2 Version")
    parser.add_argument("input", type=str, help="Breakseq2 final vcf file. Concatenate all the vcf output files into a single vcf")
    parser.add_argument("source", type=str, help="unique identifier. Fullpath to bam or samplename")
    args = parser.parse_args()
    samplename = os.path.splitext(os.path.basename(args.source))[0]
    svpfile = samplename + "_BS.svp"

    with open(args.input, 'r') as fh, open(svpfile, 'w') as fout:
        fout.write("##program=" + args.version+"\n")
        fout.write("##abbrev=BS"+"\n")
        fout.write("##source=" + args.source+"\n") 
        pullHeader(fh)
        mergeHeader1 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"
        fout.write(mergeHeader1+"\n")
        Convert(fh) 
