import sys

def main():
    filter_contigs = sys.argv[1]
    lumpy_exclude_file = open("lumpy_exclude.bed", 'w')
    delly_exclude_file = open("delly_exclude.txt", 'w')

    for line in sys.stdin:
        if line[:3] != "@SQ": 
            continue
        sequence_name = line.strip().split("SN:")[-1].split("\t")[0]
        length = int(line.strip().split("LN:")[-1].split("\t")[0])

        # Ignore the sponge contig for the hs37d5 human genome
        if filter_contigs and (sequence_name == "hs37d5" or "alt" in sequence_name or "_random" in sequence_name or "_decoy" in sequence_name):
            lumpy_exclude_file.write("%s\t%d\t%d\n" % (sequence_name, 1, length) )
            continue

        if filter_contigs and length < 1000000:
            lumpy_exclude_file.write("%s\t%d\t%d\n" % (sequence_name, 1, length) )
            delly_exclude_file.write("%s\n" % sequence_name)
            continue

        if filter_contigs and (length < 1000000 or sequence_name == "hs37d5" or "alt" in sequence_name or "_random" in sequence_name or "_decoy" in sequence_name):
            continue
        else:
            print sequence_name

    lumpy_exclude_file.close()
    delly_exclude_file.close()

main()