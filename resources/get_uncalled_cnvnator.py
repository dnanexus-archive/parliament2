import sys

for line in sys.stdin:
    if line[0] == "#":
        sys.stdout.write(line)
    else:
        gt = line.strip().split("\t")[9]
        if "./." in gt:
            sys.stdout.write(line)
