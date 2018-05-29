import os.path
import argparse

def enum(**enums):
    return type('Enum', (), enums)

""" <-- Header for breakdancer output
Chr1
Pos1
Orientation1
Chr2
Pos2
Orientation2
Type
Size    Score
num_Reads
num_Reads_lib
lupskiwgs.bam
"""

mergeHeader1 = """##INFO=<ID="SVPNAME",Number=.,Type=String,Description="unique name given to this event (for uniting with viz info)">
##INFO=<ID="O1",Number=.,Type=String,Description="orientation 1">
##INFO=<ID="O2",Number=.,Type=String,Description="orientation 2">
##INFO=<ID="TY",Number=.,Type=String,Description="type">
##INFO=<ID="SZ",Number=.,Type=Integer,Description="size">
##INFO=<ID="SC",Number=.,Type=Integer,Description="score">
##INFO=<ID="NR",Number=.,Type=Integer,Description="num reads">
##INFO=<ID="BAM",Number=.,Type=Float,Description="sample">
##INFO=<ID="TXP",Number=.,Type=String,Description="Coordinates for CTX's pair (chr:pos format)">"""

mergeHeader2 = "#CHROM\tOUTERSTART\tSTART\tINNERSTART\tINNEREND\tEND\tOUTEREND\tTYPE\tSIZE\tINFO"

COUNT = 1

def makeInfo(data, ctxChr=None, ctxPos=None):
    """
    makes all the Info key=val stuff
    """
    global COUNT
    # Use None for fields used elsewhere
    #          KEY , VAL
    keys = [ None, None, "O1", None, None, "O2", \
             "TY", "SZ", "SC", "NR", "BAM" ]
    
    myId = "%d" % (COUNT)
    COUNT += 1
    
    ret = ["SVPNAME=%s" % (myId)]
    for k,d in zip(keys, data):
        if k is not None:
            ret.append("%s=%s" % (k, str(d)))
    if ctxChr is not None:
       ret.append("TXP=%s:%d" % (ctxChr, ctxPos))
    else:
       ret.append("TXP=.")
    
    return ";".join(ret), myId

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("version", type=str, help="BD version")
    parser.add_argument("input", type=str, help="BD ctx output file")
    parser.add_argument("source", type=str, help="unique identifier. Fullpath to bam or samplename")
    args = parser.parse_args()
    
    h = {}
    s = "Chr1   Pos1    Orientation1    Chr2    Pos2    Orientation2    Type    Size    Score   num_Reads   num_Reads_lib   lupskiwgs.bam"

    for p,i in enumerate(s.split()):
        h[i] = p

    samplename = os.path.splitext(os.path.basename(args.source))[0]
    svpfile = samplename + "_BD.svp"

    with open(args.input) as fh, open(svpfile, 'w') as fout:
        fout.write("##program=" + args.version+"\n")
        fout.write("##abbrev=BD"+"\n")
        fout.write("##source=" + args.source+"\n") 
        fout.write(mergeHeader1+"\n")
        fout.write(mergeHeader2+"\n")
            
        for line in fh.readlines():
            if line.startswith("#"):
                continue
                
            data = line.split()
           
            if int(data[h["Score"]]) <= 50:
                continue 
                size = abs(int(data[h["Size"]]))
                
                if data[h["Type"]] in ["CTX", "ITX"]:
                    start = int(data[h["Pos1"]])
                    mut_type = "MIS" 
                    outerEnd = start + size
                    end = int(data[h["Pos2"]])
                    outerStart = end - size
                else:
                    points = [int(data[h["Pos1"]]), int(data[h["Pos2"]])]
                    points.sort()
                    start, stop = points

                if(data[h["Type"]] == "INV"):
                    mut_type = "MIS"
                else:
                    mut_type = str(data[h["Type"]])

                if size >= 100:
                    odata, id = makeInfo(data)
                    fout.write("%s\t.\t%d\t.\t.\t%d\t.\t%s\t%d\t%s\n" % (data[h["Chr1"]], start, stop, mut_type, size, odata))
                else:
                    #write the left
                    odata, id = makeInfo(data, data[h["Chr2"]], end)
                    fout.write("%s\t.\t%d\t.\t.\t.\t%d\t%s\t%d\t%s\n" % (data[h["Chr1"]], start, outerEnd, mut_type, size, odata))
                    #write the right
                    odata, id = makeInfo(data, data[h["Chr1"]], start)
                    fout.write("%s\t%d\t.\t.\t.\t%d\t.\t%s\t%d\t%s\n" % (data[h["Chr2"]], outerStart, end, mut_type, size, odata))
