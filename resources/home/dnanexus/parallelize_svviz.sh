#!/bin/bash

survivor_sorted=$1

grep \# survivor_sorted.vcf > header.txt

if [[ "${svviz_only_validated_candidates}" == "True" ]]; then
    echo "Only visualizing validated candidates"
    grep -v \# survivor_sorted.vcf | grep -E -h "0/1|1/1" > vcf_entries.vcf
else
    grep -v \# survivor_sorted.vcf > vcf_entries.vcf
fi

NUM_FILES=500
vcf_entries=$(wc -l < vcf_entries.vcf | tr -d ' ')

# Verify that there are VCF entries available to visualize
if [[ "${vcf_entries}" == 0 ]]; then
    # not throwing an error
    echo "No entries in the VCF to visualize. Not running svviz."
else
    ((lines_per_file = (vcf_entries + NUM_FILES - 1) / NUM_FILES))
    split --lines="${lines_per_file}" vcf_entries.vcf small_vcf.
    count=0

    for item in small_vcf*; do
        cat header.txt "${item}" > survivor_split."${count}".vcf
        echo "svviz --pair-min-mapq 30 --max-deletion-size 5000 --max-reads 10000 --fast --type batch --summary svviz_summary.tsv -b input.bam ref.fa survivor_split.${count}.vcf --export svviz_outputs" >> commands.txt
        ((count++))
    done

    threads="$(nproc)"
    threads=$((threads / 2))
    parallel --memfree 5G --retries 2 --verbose -a commands.txt eval 1>/home/dnanexus/out/log_files/svviz_logs/svviz.stdout.log 2>/home/dnanexus/out/log_files/svviz_logs/svviz.stderr.log

    cd /home/dnanexus/svviz_outputs && tar -czf /home/dnanexus/out/"${prefix}".svviz_outputs.tar.gz .
fi