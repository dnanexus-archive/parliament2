import glob, os, sys

chromosomes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "X", "Y"]

def main():
    bam_chromosomes = []
    with open("bam_chromosomes.txt", 'r') as f:
        for line in f:
            if line.strip() in chromosomes:
                bam_chromosomes.append(line.strip())

    sv_caller_chromosomes = sys.argv[1]
    with open(sv_caller_chromosomes, 'r') as f:
        tmp_chromosomes = []
        for line in f:
            tmp_chromosomes.append(line.strip())
        extra_chromosomes = list(set(bam_chromosomes)-set(tmp_chromosomes))
        for chromosome in extra_chromosomes:
            print chromosome

main()