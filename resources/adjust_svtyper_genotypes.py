import sys

for line in open(sys.argv[1], 'r'):
    if line[0] == "#" and line[1] == "#":
        sys.stdout.write(line)
    else:
        tab_split = line.strip().split("\t")[:9]
        tab_split.append(line.strip().split("\t")[-1])
        new_line = "\t".join(tab_split)
        print new_line
