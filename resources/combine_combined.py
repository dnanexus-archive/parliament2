import sys

def main():
    headers = []

    written_additional_header = False

    sample = sys.argv[2]

    for line in open(sys.argv[1], 'r'):
        if line.startswith("##"):
            if "FORMAT" in line and not written_additional_header:
                print "##INFO=<ID=CALLERS,Number=.,Type=String,Description=\"Callers that support an ALT call at this position\">"
                sys.stdout.write(line)
                written_additional_header = True
                print "##FORMAT=<ID=SP,Number=.,Type=String,Description=\"Callers that support an ALT call at this position\">"
            else:
                sys.stdout.write(line)
        elif line[0] == "#" and line[1] != "#":
            tab_split = line.strip().split("\t")
            for x in tab_split[9:]:
                if "cnvnator" in x:
                    headers.append("CNVNATOR")
                if "breakdancer" in x:
                    headers.append("BREAKDANCER")
                if "breakseq" in x:
                    headers.append("BREAKSEQ")
                if "manta" in x:
                    headers.append("MANTA")
                if "lumpy" in x:
                    headers.append("LUMPY")
                if "delly" in x:
                    headers.append("DELLY")
            print "\t".join(tab_split[:9]) + "\t%s" % sample
        else:
            tab_split = line.strip().split("\t")

            position = int(tab_split[1])
            end = tab_split[7].split("END=")[-1].split(";")[0].split("\t")[0]
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

            print "\t".join(tab_split[:10])
        
main()