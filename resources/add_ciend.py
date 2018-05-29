import sys

ci_length = int(sys.argv[1])

for line in sys.stdin:
    if line[0] == "#":
        sys.stdout.write(line)
    else:
        tab_split = line.strip().split("\t")
        if "CIEND=" not in tab_split[7]:
            tab_split[7] += ";CIEND=-%d,%d" % (ci_length, ci_length)
        if "CIPOS" not in tab_split[7]:
            tab_split[7] += ";CIPOS=-%d,%d" % (ci_length, ci_length)
        print "\t".join(tab_split)
