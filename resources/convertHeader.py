import sys

prefix = sys.argv[1]
header = ""

if isinstance(sys.argv[2:], list):
    file_list = sys.argv[2:][0]
else:
    file_list = sys.argv[2:]

for filename in file_list.split():
    try:
        inputFile = open(filename, 'r')
        if header == "":
            for line in inputFile:
                if line[0] == "#" and line[1] == "#":
                    header += line
                elif line[0] == "#" and line[1] != "#":
                    tabSplit = line.split("\t")
                    tabSplit[-1] = prefix
                    header += "\t".join(tabSplit)
                else:
                    print header
                    inputFile.close()
                    inputFile = open(filename, 'r')
                    break
        for line in inputFile:
            if line[0] != "#":
                sys.stdout.write(line)
    except:
        pass
