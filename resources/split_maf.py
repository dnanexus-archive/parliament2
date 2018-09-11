import sys

contigs = []
for x in sys.argv[2:]:
    contigs.append(x)

for line in open(sys.argv[1], 'r'):
    if line[0] == "#":
        sys.stdout.write(line)
    else:
        tab_split = line.split("\t")
        if tab_split[0] in contigs:
            sys.stdout.write(line)
