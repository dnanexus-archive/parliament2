import sys

for line in sys.stdin:
    if line.startswith('#'):
        sys.stdout.write(line)
        continue
    else:
        tab_split = line.strip().split("\t")
        if len(tab_split) == 1:
            continue
        else:
            position = int(tab_split[1])
            end = int(line.replace("CIEND","XXXXX").split("END=")[-1].split(";")[0].split("\t")[0].split(",")[0])
            chr2 = line.split("CHR2=")[-1].split(";")[0].split("\t")[0]
            chr1 = line.split("\t")[0].split("chr")[-1]
            
            if end < position and chr1 == chr2:
                tab_split[1] = str(end)
                info_fields = tab_split[7].split(";")
                for i in range(len(info_fields)):
                    if "END=" in info_fields[i]:
                        info_fields[i] = "END=%d" % position
                tab_split[7] = ";".join(info_fields)
                sys.stdout.write("\t".join(tab_split))
                sys.stdout.write('\n')
            else:
                sys.stdout.write(line.strip())
                sys.stdout.write('\n')
