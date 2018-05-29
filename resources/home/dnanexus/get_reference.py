def main():
    reference_chosen = False
    with open("ref.fa", 'r') as f:
        chrs = set()
        for line in f:
            if line.startswith(">chr1") and "LN:248956422" in line:
                print "hg38"
                reference_chosen = True
                break
            if line.startswith('>'):
                chrs.add(line)
                if not line.startswith('>chr'):
                    print "b37"
                    reference_chosen = True
                    break

    if not reference_chosen:
        if len(chrs) == 195:
            print "hg38"
        else:
            print "hg19"

main()