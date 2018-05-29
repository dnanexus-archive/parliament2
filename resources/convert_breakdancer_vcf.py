import sys

print "##fileformat=VCFv4.0"
print "##source=Breakdancer"
print "##INFO=<ID=END,Number=1,Type=Integer,Description=\"End position of the variant described in this record\">"
print "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tSAMPLE"

for line in sys.stdin:
    if line[0] == "#":
        continue
    tab_split = line.strip().split("\t")
    c1 = tab_split[0]
    c2 = tab_split[3]
    if c1 != c2:
        continue
    pos = int(tab_split[1])
    hi = int(tab_split[4])
    svtype = tab_split[6]
    if svtype != "INS" and svtype != "DEL" and svtype != "INV":
        continue
    print "%s\t%d\t.\tN\t.\t.\t.\tEND=%d;CIPOS=-20,20;CIEND=-20,20;SVTYPE=%s\tGT\t./." % (c1, min(pos, hi), max(pos, hi), svtype)