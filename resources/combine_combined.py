import sys

def main():
    headers = []

    written_additional_header = False

    sample = sys.argv[2]
    for line in open(sys.argv[3], 'r'):
        if "cnvnator" in line:
            headers.append("CNVNATOR")
        elif "breakdancer" in line:
            headers.append("BREAKDANCER")
        elif "breakseq" in line:
            headers.append("BREAKSEQ")
        elif "manta" in line:
            headers.append("MANTA")
        elif "lumpy" in line:
            headers.append("LUMPY")
        elif "delly" in line:
            headers.append("DELLY")
        else:
            headers.append(line.strip())
            
    deletion_quality_mappings = { "lt300": {}, "300to1000": {}, "1kbplus": {}, "all": {}}

    for line in open(sys.argv[4]):
        size_split = line.split("_")
        size_class = size_split[0]
        entry_split = size_split[1].strip().split("=")
        caller_technologies = entry_split[0].split("&")
        caller_technologies.sort()
        if int(entry_split[1]) == 0: 
            deletion_quality_mappings[size_class][",".join(caller_technologies)] = "1"
        else:
            deletion_quality_mappings[size_class]["-".join(caller_technologies)] = int(entry_split[1])

    for line in open(sys.argv[1], 'r'):
        if line.startswith("##"):
            if "FORMAT" in line and not written_additional_header:
                print "##INFO=<ID=CALLERS,Number=.,Type=String,Description=\"Callers that support an ALT call at this position\">"
                print line
                written_additional_header = True
            else:
                print line
        elif line[0] == "#" and line[1] != "#":
            tab_split = line.strip().split("\t")
            print "\t".join(tab_split[:9]) + "\t%s" % sample
        else:
            tab_split = line.strip().split("\t")

            position = int(tab_split[1])
            end = tab_split[7].replace("CIEND","XXXXX").split("END=")[-1].split(";")[0].split("\t")[0]
            end_position = int(end)
            if end_position < position:
                new_end = str(position)
                new_start = end
                tab_split[1] = new_start
                tab_split[7].replace("END=%s" % end, "END=%s" % new_end)

            support = ""
            het = 0
            hom = 0
            ref = 0
            if "chr" not in tab_split[0]:
                tab_split[0] = "chr" + tab_split[0]
            for i in range(len(tab_split[9:])):
                if "0/1" in tab_split[9+i] or "1/1" in tab_split[9+i] or "./1" in tab_split[9+i]:
                    if "0/1" in tab_split[9+i] or "./1" in tab_split[9+i]:
                        het += 1
                    if "1/1" in tab_split[9+i] or "./1" in tab_split[9+i]:
                        hom += 1
                    if "0/0" in tab_split[9+i]:
                        ref += 1
                    if headers[i] not in support:
                        support += ",%s" % headers[i]
            if len(support) > 0:
                tab_split[7] += ";CALLERS=%s" % support.lstrip(",")
            else:
                support = "."
                
            tab_split[8] = "GT:SP"
            if het == 0 and hom == 0:
                if ref > 0:
                    tab_split[9] = "0/0:"
                else:
                    tab_split[9] = "./.:"
            elif hom > het:
                tab_split[9] = "1/1:"
            else:
                tab_split[9] = "0/1:"
            
            tab_split[9] += support.lstrip(",")

            if "SVTYPE=DEL" in line:
                try:
                    size = end_position - position
                    if size < 300:
                        size_range = "lt300"
                    elif size < 1000:
                        size_range = "300to1000"
                    else:
                        size_range = "1kbplus"
                except:
                    size_range = "all"


                callers = support.lstrip(",").split(",")
                callers.sort()
                if deletion_quality_mappings[size_range].get(",".join(callers)) != None:
                    tab_split[5] = str(deletion_quality_mappings[size_range].get(",".join(callers)))
                    
            print "\t".join(tab_split[:10])
        
main()
