#!/usr/bin/env bash

illumina_bam=$1
illumina_bai=$2
gatk_jar=$3
ref_fasta=$4
ref_index=$5
prefix=$6
filter_short_contigs=$7
run_breakdancer=$8
run_breakseq=$9
run_manta=${10}
run_cnvnator=${11}
run_lumpy=${12}
run_delly_deletion=${13}
run_delly_insertion=${14}
run_delly_inversion=${15}
run_delly_duplication=${16}
run_genotype_candidates=${17}
run_atlas=${18}
run_stats=${19}
run_svviz=${20}
svviz_only_validated_candidates=${21}
dnanexus=${22}

check_threads(){
    breakdancer_processes=$(top -n 1 -b -d 10 | grep -c breakdancer)
    cnvnator_processes=$(top -n 1 -b -d 10 | grep -c cnvnator)
    sambamba_processes=$(top -n 1 -b -d 10 | grep -c sambamba)
    manta_processes=$(top -n 1 -b -d 10 | grep -c manta)
    breakseq_processes=$(top -n 1 -b -d 10 | grep -c breakseq)
    delly_processes=$(top -n 1 -b -d 10 | grep -c delly)
    lumpy_processes=$(top -n 1 -b -d 10 | grep -c lumpy)
    atlas_processes=$(top -n 1 -b -d 10 | grep -c atlas)
    indel_realigner_processes=$(top -n 1 -b -d 10 | grep -c java)
    verify_processes=$(top -n 1 -b -d 10 | grep -c verifyBamID)
    alignstats_processes=$(top -n 1 -b -d 10 | grep -c alignstats)
    active_threads=$(python /getThreads.py "${breakdancer_processes}" "${cnvnator_processes}" "${sambamba_processes}" "${manta_processes}" "${breakseq_processes}" "${delly_processes}" "${lumpy_processes}" "${atlas_processes}" "${indel_realigner_processes}" "${verify_processes}" "${alignstats_processes}")

    while [[ $active_threads -ge $(nproc) ]]; do
        sleep 60
        breakdancer_processes=$(top -n 1 -b -d 10 | grep -c breakdancer)
        cnvnator_processes=$(top -n 1 -b -d 10 | grep -c cnvnator)
        sambamba_processes=$(top -n 1 -b -d 10 | grep -c sambamba)
        manta_processes=$(top -n 1 -b -d 10 | grep -c manta)
        breakseq_processes=$(top -n 1 -b -d 10 | grep -c breakseq)
        delly_processes=$(top -n 1 -b -d 10 | grep -c delly)
        lumpy_processes=$(top -n 1 -b -d 10 | grep -c lumpy)
        atlas_processes=$(top -n 1 -b -d 10 | grep -c atlas)
        indel_realigner_processes=$(top -n 1 -b -d 10 | grep -c java)
        verify_processes=$(top -n 1 -b -d 10 | grep -c verifyBamID)
        alignstats_processes=$(top -n 1 -b -d 10 | grep -c alignstats)
        active_threads=$(python /getThreads.py "${breakdancer_processes}" "${cnvnator_processes}" "${sambamba_processes}" "${manta_processes}" "${breakseq_processes}" "${delly_processes}" "${lumpy_processes}" "${atlas_processes}" "${indel_realigner_processes}" "${verify_processes}" "${alignstats_processes}")
        echo "Checking threads"
    done
}

echo "Running Parliament2 at time $(date)"

if [[ ! -f "${illumina_bam}" ]] || [[ ! -f "${ref_fasta}" ]]; then
    if [[ "$dnanexus" == "True" ]]; then
        dx-jobutil-report-error "ERROR: An invalid (nonexistent) input file has been specified."
    else
        echo "ERROR: An invalid (nonexistent) input file has been specified."
        exit 1
    fi
fi

cp "${ref_fasta}" ref.fa

if [[ "${run_breakdancer}" == "False" ]] && [[ "${run_breakseq}" == "False" ]] && [[ "${run_manta}" == "False" ]] && [[ "${run_cnvnator}" == "False" ]] && [[ "${run_lumpy}" == "False" ]] && [[ "${run_delly_deletion}" == "False" ]] && [[ "${run_delly_insertion}" == "False" ]] && [[ "${run_delly_inversion}" == "False" ]] && [[ "${run_delly_duplication}" == "False" ]] && [[ "${run_atlas}" == "False" ]]; then
    echo "WARNING: Did not detect any variant calling modules requested by the user through command-line flags."
    echo "Running with default SV modules: Breakdancer, Breakseq, Manta, CNVnator, Lumpy, and Delly Deletion"
    run_breakdancer="True"
    run_breakseq="True"
    run_manta="True"
    run_cnvnator="True"
    run_lumpy="True"
    run_delly_deletion="True"
fi

if [[ "${ref_index}" == "None" ]]; then
    samtools faidx ref.fa &
else
    cp "${ref_index}" ref.fa.fai
fi

ref_genome=$(python /home/dnanexus/get_reference.py)
lumpy_exclude_string=""
if [[ "${ref_genome}" == "b37" ]]; then
    lumpy_exclude_string="-x b37.bed"
elif [[ "$ref_genome" == "hg19" ]]; then
    lumpy_exclude_string="-x hg19.bed"
else
    lumpy_exclude_string="-x hg38.bed"
fi

export lumpy_scripts="/home/dnanexus/lumpy-sv/scripts"

# Get extension and threads
extn=${illumina_bam##*.}
threads="$(nproc)"
threads=$((threads - 3))

echo "Set up and index BAM/CRAM"

# Check if BAM file has already been processed -- if so, continue
if [[ -f "/home/dnanexus/in/done.txt" ]]; then
    echo "BAM file and index both exist in the mounted volume; continuing"
else
    # Allow for CRAM files
    if [[ "${extn}" == "cram" ]] || [[ "${extn}" == "CRAM" ]]; then
        echo "CRAM file input"
        mkfifo tmp_input.bam
        samtools view "${illumina_bam}" -bh -@ "${threads}" -T ref.fa -o - | tee tmp_input.bam > input.bam & 
        samtools index tmp_input.bam
        wait
        mv tmp_input.bam.bai input.bam.bai
        rm tmp_input.bam

        mv input.bam /home/dnanexus/in/input.bam
        mv input.bam.bai /home/dnanexus/in/input.bam.bai
    elif [[ "${illumina_bai}" == "None" ]]; then
        echo "BAM file input, no index exists"
        cp "${illumina_bam}" input.bam
        samtools index input.bam

        mv input.bam.bai /home/dnanexus/in/input.bam.bai
    else
        echo "BAM file input, index exists"
        cp "${illumina_bam}" input.bam
        mv "${illumina_bai}" input.bam.bai
    fi

    touch /home/dnanexus/in/done.txt
fi

rm "${illumina_bam}" && touch "${illumina_bam}"
ln -s /home/dnanexus/in/input.bam /home/dnanexus/input.bam
ln -s /home/dnanexus/in/input.bam.bai /home/dnanexus/input.bam.bai

wait

echo "Generate contigs"

samtools view -H input.bam | python /getContigs.py "${filter_short_contigs}" > contigs.txt

mkdir -p /home/dnanexus/out/log_files/

# Frontloading IndelRealigner
if [[ "${run_atlas}" == "True" ]]; then
    echo "Creating fasta dict file"
    mkdir -p /home/dnanexus/out/log_files/create_seq_dict/
    java -jar CreateSequenceDictionary.jar REFERENCE=ref.fa OUTPUT=ref.dict 1> /home/dnanexus/out/log_files/create_seq_dict/"${prefix}".picard_dict.stdout.log 2> /home/dnanexus/out/log_files/create_seq_dict/"${prefix}".picard_dict.stderr.log

    mkdir -p /home/dnanexus/out/log_files/realigner_target_creator/
    mkdir -p /home/dnanexus/out/log_files/indel_realigner/
    mkdir -p /home/dnanexus/out/log_files/xatlas/
fi

if [[ "${run_stats}" == "True" ]]; then
    mkdir -p /home/dnanexus/out/stats
    mkdir -p /home/dnanexus/out/log_files/verify_bam_id/

    echo "Running verifyBamID"
    verifyBamID --vcf maf.0.vcf --bam input.bam --out /home/dnanexus/out/stats/"${prefix}".chr1-8 --ignoreRG 1> /home/dnanexus/out/log_files/verify_bam_id/"${prefix}".verify.0.stout.log 2> /home/dnanexus/out/log_files/verify_bam_id/"${prefix}".verify.0.stderr.log &
    verifyBamID --vcf maf.1.vcf --bam input.bam --out /home/dnanexus/out/stats/"${prefix}".chr9-15 --ignoreRG 1> /home/dnanexus/out/log_files/verify_bam_id/"$prefix".verify.1.stout.log 2> /home/dnanexus/out/log_files/verify_bam_id/"${prefix}".verify.1.stderr.log &
    verifyBamID --vcf maf.2.vcf --bam input.bam --out /home/dnanexus/out/stats/"${prefix}".chr16-Y --ignoreRG 1> /home/dnanexus/out/log_files/verify_bam_id/"$prefix".verify.2.stout.log 2> /home/dnanexus/out/log_files/verify_bam_id/"${prefix}".verify.2.stderr.log &

    echo "Running alignstats"
    mkdir -p /home/dnanexus/out/log_files/alignstats/
    alignstats -v -p -F 2048 -i input.bam -o "${prefix}".AlignStatsReport.txt -r GRCh38_full_analysis_set_plus_decoy_hla.bed -t HG38_lom_vcrome2.1_with_PKv2.bed -m GRCh38_1000Genomes_N_regions.bed 1> /home/dnanexus/out/log_files/alignstats/"${prefix}".alignstats.stdout.log 2> /home/dnanexus/out/log_files/alignstats/"${prefix}".alignstats.stderr.log &
    samtools flagstat input.bam > "${prefix}".flagstats &
fi

if [[ "${run_breakseq}" == "True" || "${run_manta}" == "True" ]]; then
    echo "Launching jobs that cannot be parallelized by contig"
fi

# JOBS THAT CANNOT BE PARALLELIZED BY CONTIG
# BREAKSEQ2
if [[ "${run_breakseq}" == "True" ]]; then
    mkdir -p /home/dnanexus/out/log_files/breakseq/
    echo "Running BreakSeq"
    bplib="/breakseq2_bplib_20150129/breakseq2_bplib_20150129.gff"
    work="breakseq2"
    timeout 6h ./breakseq2-2.2/scripts/run_breakseq2.py --reference ref.fa \
        --bams input.bam --work "${work}" \
        --bwa /usr/local/bin/bwa --samtools /usr/local/bin/samtools \
        --bplib_gff "${bplib}" \
        --nthreads "$(nproc)" --bplib_gff "${bplib}" \
        --sample "$prefix" 1> /home/dnanexus/out/log_files/breakseq/"${prefix}".breakseq.stdout.log 2> /home/dnanexus/out/log_files/breakseq/"${prefix}".breakseq.stderr.log &
fi

# MANTA
if [[ "${run_manta}" == "True" ]]; then
    echo "Running Manta"
    mkdir -p /home/dnanexus/out/log_files/manta/
    timeout 6h runManta 1> /home/dnanexus/out/log_files/manta/"${prefix}".manta.stdout.log 2> /home/dnanexus/out/log_files/manta/"${prefix}".manta.stderr.log &
fi

# PREPARE FOR BREAKDANCER
if [[ "${run_breakdancer}" == "True" ]]; then
    timeout 2h /breakdancer/cpp/bam2cfg -o breakdancer.cfg input.bam
fi

concat_breakdancer_cmd=
concat_cnvnator_cmd=

count=0
delly_deletion_concat=""
delly_inversion_concat=""
delly_duplication_concat=""
delly_insertion_concat=""
lumpy_merge_command=""

if [[ "${run_delly_deletion}" == "True" ]] || [[ "${run_delly_insertion}" == "True" ]] || [[ "${run_delly_inversion}" == "True" ]] || [[ "${run_delly_duplication}" == "True" ]]; then
   run_delly="True"
fi

count=0
# Process management for launching jobs
if [[ "${run_cnvnator}" == "True" ]] || [[ "${run_delly}" == "True" ]] || [[ "${run_breakdancer}" == "True" ]] || [[ "${run_lumpy}" == "True" ]] || [[ "${run_atlas}" == "True" ]]; then
    echo "Launching jobs parallelized by contig"
    mkdir -p /home/dnanexus/out/log_files/breakdancer/
    mkdir -p /home/dnanexus/out/log_files/cnvnator/
    mkdir -p /home/dnanexus/out/log_files/delly_deletion/
    mkdir -p /home/dnanexus/out/log_files/delly_duplication/
    mkdir -p /home/dnanexus/out/log_files/delly_insertion/
    mkdir -p /home/dnanexus/out/log_files/delly_inversion/
    mkdir -p /home/dnanexus/out/log_files/lumpy/

    while read -r contig; do
        echo "Checking contig ${contig}"
        if [[ $(samtools view input.bam "${contig}" | head -n 20 | wc -l) -ge 10 ]]; then
            echo "Running on contig ${contig}"
            count=$((count + 1))
            if [[ "${run_breakdancer}" == "True" ]]; then
                echo "Running Breakdancer for contig ${contig}"
                timeout 4h /breakdancer/cpp/breakdancer-max breakdancer.cfg input.bam -o "${contig}" 1> breakdancer-"${count}".ctx 2> /home/dnanexus/out/log_files/breakdancer/"${prefix}".breakdancer."${contig}".stderr.log &
                concat_breakdancer_cmd="${concat_breakdancer_cmd} breakdancer-${count}.ctx"
            fi

            if [[ "${run_cnvnator}" == "True" ]]; then
                echo "Running CNVnator for contig ${contig}"
                runCNVnator "${contig}" "${count}" 1> /home/dnanexus/out/log_files/cnvnator/"${prefix}".cnvnator."${contig}"stdout.log 2> /home/dnanexus/out/log_files/cnvnator/"${prefix}".cnvnator."${contig}".stderr.log &
                concat_cnvnator_cmd="${concat_cnvnator_cmd} output.cnvnator_calls-${count}"
            fi

            if [[ "${run_atlas}" == "True" ]]; then
                bash ./run_realign_atlas.sh input.bam ref.fa "${gatk_jar}" "${prefix}" "${contig}" &
            fi

            if [[ "${run_delly}" == "True" ]] || [[ "${run_lumpy}" == "True" ]]; then
                echo "Running sambamba view"
                timeout 2h sambamba view -h -f bam input.bam "${contig}" > chr."${count}".bam
                echo "Running sambamba index"
                sambamba index chr."${count}".bam
            fi

            if [[ "$run_delly_deletion" == "True" ]]; then  
                echo "Running Delly (deletions) for contig ${contig}"
                timeout 6h delly -t DEL -o "${count}".delly.deletion.vcf -g ref.fa chr."${count}".bam 1> /home/dnanexus/out/log_files/delly_deletion/"${prefix}".delly_deletion."${contig}"stdout.log 2> /home/dnanexus/out/log_files/delly_deletion/"${prefix}".delly_deletion."${contig}".stderr.log & 
                delly_deletion_concat="$delly_deletion_concat $count.delly.deletion.vcf"
            fi

            if [[ "$run_delly_inversion" == "True" ]]; then 
                echo "Running Delly (inversions) for contig ${contig}"
                timeout 6h delly -t INV -o "${count}".delly.inversion.vcf -g ref.fa chr."${count}".bam 1> /home/dnanexus/out/log_files/delly_inversion/"${prefix}".delly_inversion."${contig}"stdout.log 2> /home/dnanexus/out/log_files/delly_inversion/"${prefix}".delly_inversion."${contig}".stderr.log &
                delly_inversion_concat="$delly_inversion_concat $count.delly.inversion.vcf"
            fi

            if [[ "$run_delly_duplication" == "True" ]]; then 
                echo "Running Delly (duplications) for contig ${contig}"
                timeout 6h delly -t DUP -o "${count}".delly.duplication.vcf -g ref.fa chr."${count}".bam 1> /home/dnanexus/out/log_files/delly_duplication/"${prefix}".delly_duplication."${contig}"stdout.log 2> /home/dnanexus/out/log_files/delly_duplication/"${prefix}".delly_duplication."${contig}".stderr.log &
                delly_duplication_concat="$delly_duplication_concat $count.delly.duplication.vcf"
            fi

            if [[ "$run_delly_insertion" == "True" ]]; then 
                echo "Running Delly (insertions) for contig ${contig}"
                timeout 6h delly -t INS -o "${count}".delly.insertion.vcf -g ref.fa chr."${count}".bam 1> /home/dnanexus/out/log_files/delly_insertion/"${prefix}".delly_insertion."${contig}"stdout.log 2> /home/dnanexus/out/log_files/delly_insertion/"${prefix}".delly_insertion."${contig}".stderr.log &
                delly_insertion_concat="$delly_insertion_concat $count.delly.insertion.vcf"
            fi
            
            if [[ "$run_lumpy" == "True" ]]; then
                echo "Running Lumpy for contig ${contig}"
                timeout 6h ./lumpy-sv/bin/lumpyexpress -B chr."${count}".bam -o lumpy."${count}".vcf "${lumpy_exclude_string}" -k 1> /home/dnanexus/out/log_files/lumpy/"${prefix}".lumpy."${contig}"stdout.log 2> /home/dnanexus/out/log_files/lumpy/"${prefix}".lumpy."${contig}".stderr.log &
                lumpy_merge_command="$lumpy_merge_command lumpy.$count.vcf"
            fi

            check_threads
        fi
    done < contigs.txt
fi

wait

mv contigs.txt /home/dnanexus/out/"${prefix}".contigs.txt
echo "All structural variant callers done running"

# Only install SVTyper if necessary
if [[ "${run_genotype_candidates}" == "True" ]]; then
    pip install git+https://github.com/hall-lab/svtyper.git -q &
fi

# Uploading stats and xAtlas outputs
(if [[ "${run_stats}" == "True" ]]; then
    echo "Uploading stats outputs"
    if [[ ! -f "${prefix}".AlignStatsReport.txt && ! -f "${prefix}".flagstats ]]; then
        echo "No outputs of alignstats found. Continuing."
    else
        cp "${prefix}".AlignStatsReport.txt /home/dnanexus/out/stats/"${prefix}".AlignStatsReport.txt
        cp "${prefix}".flagstats /home/dnanexus/out/stats/"${prefix}".flagstats
    fi
fi) &

(if [[ "${run_atlas}" == "True" ]]; then
    echo "Uploading xAtlas outputs"
    if [[ -z $(find . -name "*_indel.vcf") ]] && [[ -z $(find . -name "*_snp.vcf") ]] ; then
        echo "No outputs of xAtlas found. Continuing."
    else
        mkdir -p /home/dnanexus/out/atlas
        cat ./*_indel.vcf | vcf-sort -c | uniq | bgzip > "${prefix}"_indel.vcf.gz; tabix "${prefix}"_indel.vcf.gz
        cat ./*_snp.vcf | vcf-sort -c | uniq | bgzip > "${prefix}"_snp.vcf.gz; tabix "${prefix}"_snp.vcf.gz

        cp "${prefix}"_snp.vcf.gz /home/dnanexus/out/atlas/"${prefix}".atlas.snp.vcf.gz
        cp "${prefix}"_snp.vcf.gz.tbi /home/dnanexus/out/atlas/"${prefix}".atlas.snp.vcf.gz.tbi
        cp "${prefix}"_indel.vcf.gz /home/dnanexus/out/atlas/"${prefix}".atlas.indel.vcf.gz
        cp "${prefix}"_indel.vcf.gz.tbi /home/dnanexus/out/atlas/"${prefix}".atlas.indel.vcf.gz.tbi
    fi
fi) &

echo "Converting results to VCF format"
mkdir -p /home/dnanexus/out/sv_caller_results/

(if [[ "${run_lumpy}" == "True" ]]; then
    echo "Convert Lumpy results to VCF format"
    python /convertHeader.py "${prefix}" "${lumpy_merge_command}" | vcf-sort -c | uniq > lumpy.vcf

    if [[ -f lumpy.vcf ]]; then
        cp lumpy.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".lumpy.vcf

        python /vcf2bedpe.py -i lumpy.vcf -o lumpy.gff
        python /Lumpy2merge.py lumpy.gff "${prefix}" 1.0
    else
        echo "No outputs of Lumpy found. Continuing."
    fi
fi) &

(if [[ "${run_manta}" == "True" ]]; then
    echo "Convert Manta results to VCF format"
    if [[ ! -f manta/results/variants/diploidSV.vcf.gz && ! -f manta/results/stats/alignmentStatsSummary.txt ]]; then
        echo "No outputs of Manta found. Continuing."
    else  
        cp manta/results/variants/diploidSV.vcf.gz /home/dnanexus/out/sv_caller_results/"${prefix}".manta.diploidSV.vcf.gz
        mv manta/results/variants/diploidSV.vcf.gz .
        gunzip diploidSV.vcf.gz
        python /Manta2merge.py 1.0 diploidSV.vcf "${prefix}"
        cp manta/results/stats/alignmentStatsSummary.txt /home/dnanexus/out/sv_caller_results/"${prefix}".manta.alignmentStatsSummary.txt
    fi

fi) &

(if [[ "${run_breakdancer}" == "True" ]] && [[ -n "${concat_breakdancer_cmd}" ]]; then
    echo "Convert Breakdancer results to VCF format"
    # cat contents of each file into output file: lack of quotes intentional
    cat ${concat_breakdancer_cmd} > breakdancer.output

    if [[ -f breakdancer.output ]]; then
        cp breakdancer.output /home/dnanexus/out/sv_caller_results/"${prefix}".breakdancer.ctx

        python /BreakDancer2Merge.py 1.0 breakdancer.output "${prefix}"

        python /convert_breakdancer_vcf.py < breakdancer.output > breakdancer.vcf
        cp breakdancer.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".breakdancer.vcf
    else
        echo "No outputs of Breakdancer found. Continuing."
    fi
fi) &

(if [[ "${run_cnvnator}" == "True" ]] && [[ -n "${concat_cnvnator_cmd}" ]]; then
    echo "Convert CNVnator results to VCF format"
    # cat contents of each file into output file: lack of quotes intentional
    cat ${concat_cnvnator_cmd} > cnvnator.output

    if [[ -f cnvnator.output ]]; then
        perl /usr/utils/cnvnator2VCF.pl cnvnator.output > cnvnator.vcf

        cp cnvnator.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".cnvnator.vcf
        cp cnvnator.output /home/dnanexus/out/sv_caller_results/"${prefix}".cnvnator.output
    else
        echo "No outputs of CNVnator found. Continuing."
    fi
fi) &

(if [[ "${run_breakseq}" == "True" ]]; then
    echo "Convert Breakseq results to VCF format"
    if [[ -z $(find "${work}" -name "*.log") ]]; then
        echo "No Breakseq log files found."
    else
        cd "${work}" || return
        find ./*.log | tar -zcvf log.tar.gz -T -
        rm -rf ./*.log
        mv log.tar.gz /home/dnanexus/out/log_files/breakseq.log.tar.gz
        cd /home/dnanexus || return
    fi

    if [[ ! -f breakseq2/breakseq_genotyped.gff && ! -f breakseq2/breakseq.vcf.gz && ! -f breakseq2/final.bam ]]; then
        echo "No outputs of Breakseq found. Continuing."
    else
        mv breakseq2/breakseq.vcf.gz .
        gunzip breakseq.vcf.gz

        cp breakseq2/breakseq_genotyped.gff /home/dnanexus/out/sv_caller_results/"${prefix}".breakseq.gff
        cp breakseq.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".breakseq.vcf
        cp breakseq2/final.bam /home/dnanexus/out/sv_caller_results/"${prefix}".breakseq.bam
    fi
fi) &

(if [[ "${run_delly_deletion}" == "True" ]]; then 
    echo "Convert Delly deletion results to VCF format"
    python /convertHeader.py "${prefix}" "${delly_deletion_concat}" | vcf-sort -c | uniq > delly.deletion.vcf

    if [[ -f delly.deletion.vcf ]]; then
        cp delly.deletion.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".delly.deletion.vcf
    else
        echo "No Delly deletion results found. Continuing."
    fi
fi) &

(if [[ "${run_delly_inversion}" == "True" ]]; then
    echo "Convert Delly inversion results to VCF format"
    python /convertHeader.py "${prefix}" "${delly_inversion_concat}" | vcf-sort -c | uniq > delly.inversion.vcf

    if [[ -f delly.inversion.vcf ]]; then
        cp delly.inversion.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".delly.inversion.vcf
    else
        echo "No Delly inversion results found. Continuing."
    fi
fi) &

(if [[ "${run_delly_duplication}" == "True" ]]; then
    echo "Convert Delly duplication results to VCF format"
    python /convertHeader.py "${prefix}" "${delly_duplication_concat}" | vcf-sort -c | uniq > delly.duplication.vcf

    if [[ -f delly.duplication.vcf ]]; then
        cp delly.duplication.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".delly.duplication.vcf
    else
        echo "No Delly duplication results found. Continuing."
    fi
fi) &

(if [[ "${run_delly_insertion}" == "True" ]]; then
    echo "Convert Delly insertion results to VCF format"
    python /convertHeader.py "${prefix}" "${delly_insertion_concat}" | vcf-sort -c | uniq > delly.insertion.vcf

    if [[ -f delly.insertion.vcf ]]; then
        cp delly.insertion.vcf /home/dnanexus/out/sv_caller_results/"${prefix}".delly.insertion.vcf
    else
        echo "No Delly insertion results found. Continuing."
    fi
fi) &

wait

if [[ "${run_atlas}" == "True" ]]; then
    rm ./*_indel.vcf
    rm ./*_snp.vcf
fi

find /home/dnanexus/out/log_files/ -type d -empty -delete
find /home/dnanexus/out/log_files/ -maxdepth 1 -mindepth 1 -type d -exec tar czf {}.tar.gz {} --remove-files \;

# Run SVtyper and SVviz
if [[ "${run_genotype_candidates}" == "True" ]]; then
    echo "Running SVTyper"

    set -e
    # Verify that there are VCF files available
    if [[ -z $(find . -name "*.vcf") ]]; then
        if [[ "${dnanexus}" == "True" ]]; then
            dx-jobutil-report-error "ERROR: SVTyper requested, but candidate VCF files required to genotype. No VCF files found."
        else
            echo "ERROR: SVTyper requested, but candidate VCF files required to genotype. No VCF files found."
            exit 1
        fi
    fi
    set +e

    # SVviz and BreakSeq have mutually exclusive versions of pysam required, so
    # SVviz is only installed later and if necessary
    if [[ "${run_svviz}" == "True" ]]; then
        pip install svviz -q &
    fi

    mkdir -p /home/dnanexus/out/svtyped_vcfs/

    i=0
    # Breakdancer
    if [[ "${run_breakdancer}" == "True" ]]; then
        echo "Running SVTyper on Breakdancer outputs"
        mkdir -p /home/dnanexus/svtype_breakdancer
        if [[ -f /home/dnanexus/breakdancer.vcf ]]; then
            bash ./parallelize_svtyper.sh /home/dnanexus/breakdancer.vcf svtype_breakdancer /home/dnanexus/"${prefix}".breakdancer.svtyped.vcf input.bam
        else
            "No Breakdancer VCF file found. Continuing."
        fi
    fi

    # Breakseq
    if [[ "${run_breakseq}" == "True" ]]; then
        echo "Running SVTyper on BreakSeq outputs"
        mkdir -p /home/dnanexus/svtype_breakseq
        if [[ -f /home/dnanexus/breakseq.vcf ]]; then
            bash ./parallelize_svtyper.sh /home/dnanexus/breakseq.vcf svtype_breakseq /home/dnanexus/"${prefix}".breakseq.svtyped.vcf input.bam
        else
            echo "No BreakSeq VCF file found. Continuing."
        fi
    fi

    # CNVnator
    if [[ "${run_cnvnator}" == "True" ]]; then
        echo "Running SVTyper on CNVnator outputs"
        mkdir -p /home/dnanexus/svtype_cnvnator
        if [[ -f /home/dnanexus/cnvnator.vcf ]]; then
            python /get_uncalled_cnvnator.py | python /add_ciend.py 1000 > /home/dnanexus/cnvnator.ci.vcf < cnvnator.vcf
            bash ./parallelize_svtyper.sh /home/dnanexus/cnvnator.vcf svtype_cnvnator "${prefix}".cnvnator.svtyped.vcf input.bam
        else
            echo "No CNVnator VCF file found. Continuing."
        fi
    fi

    # Delly
    if [[ "${run_delly}" == "True" ]]; then
        echo "Running SVTyper on Delly outputs"
        if [[ -z $(find . -name "delly*vcf") ]]; then
            echo "No Delly VCF file found. Continuing."
        else
            for item in delly*vcf; do
                mkdir -p /home/dnanexus/svtype_delly_"$i"
                bash ./parallelize_svtyper.sh /home/dnanexus/"${item}" svtype_delly_"$i" /home/dnanexus/delly.svtyper."$i".vcf input.bam
                i=$((i + 1))
            done

            grep \# delly.svtyper.0.vcf > "${prefix}".delly.svtyped.vcf

            for item in delly.svtyper*.vcf; do
                grep -v \# "${item}" >> "${prefix}".delly.svtyped.vcf
            done
        fi
    fi

    # Lumpy
    if [[ "${run_lumpy}" == "True" ]]; then
        echo "Running SVTyper on Lumpy outputs"
        mkdir -p /home/dnanexus/svtype_lumpy
        if [[ -f /home/dnanexus/lumpy.vcf ]]; then
            bash ./parallelize_svtyper.sh /home/dnanexus/lumpy.vcf svtype_lumpy /home/dnanexus/"${prefix}".lumpy.svtyped.vcf input.bam
        else
            echo "No Lumpy VCF file found. Continuing."
        fi
    fi

    # Manta
    if [[ "${run_manta}" == "True" ]]; then
        echo "Running SVTyper on Manta outputs"
        if [[ -f diploidSV.vcf ]]; then
            mv diploidSV.vcf /home/dnanexus/"${prefix}".manta.svtyped.vcf
            echo /home/dnanexus/"${prefix}".manta.svtyped.vcf >> survivor_inputs
        else
            echo "No Manta VCF file found. Continuing."
        fi
    fi

    wait

    # Prepare inputs for SURVIVOR
    echo "Preparing inputs for SURVIVOR"
    for item in *svtyped.vcf; do
        python /adjust_svtyper_genotypes.py "${item}" | vcf-sort -c > adjusted.vcf
        mv adjusted.vcf "${item}"
        echo "${item}" >> survivor_inputs
    done

    # Prepare SVtyped VCFs for upload
    for item in *svtyped.vcf; do
        cp "${item}" /home/dnanexus/out/svtyped_vcfs/"${item}"
    done

    # Run SURVIVOR
    echo "Running SURVIVOR"
    survivor merge survivor_inputs 1000 1 1 0 0 10 survivor.output.vcf

    # Prepare SURVIVOR outputs for upload
    vcf-sort -c > survivor_sorted.vcf < survivor.output.vcf
    python /combine_combined.py survivor_sorted.vcf "${prefix}" survivor_inputs /all.phred.txt | python /correct_max_position.py > /home/dnanexus/out/"${prefix}".combined.genotyped.vcf

    # Run svviz
    if [[ "${run_svviz}" == "True" ]]; then
        echo "Running svviz"
        mkdir -p /home/dnanexus/svviz_outputs/

        grep \# survivor_sorted.vcf > header.txt

        if [[ "${svviz_only_validated_candidates}" == "True" ]]; then
            echo "Only visualizing validated candidates"
            grep -v \# survivor_sorted.vcf | grep -E -h "0/1|1/1" > vcf_entries.vcf
        else
            grep -v \# survivor_sorted.vcf > vcf_entries.vcf
        fi

        vcf_entries=$(wc -l < vcf_entries.vcf | tr -d ' ')

        # Verify that there are VCF entries available to visualize
        if [[ "${vcf_entries}" == 0 ]]; then
            # not throwing an error
            echo "No entries in the VCF to visualize. Not running svviz."
        else
            threads=$(nproc)
            threads=$(( threads \* 4 ))
            if [[ "${vcf_entries}" -ge "${threads}" ]]; then
                lines=$(("${vcf_entries}" / "${threads}"))
                split -d -a 5 -l "${lines}" vcf_entries.vcf small_vcf.
            fi
            count=0

            for item in small_vcf*; do
                cat header.txt "${item}" > survivor_split."${count}".vcf
                echo "svviz --pair-min-mapq 30 --max-deletion-size 5000 --max-reads 10000 --fast --type batch --summary svviz_summary.tsv -b input.bam ref.fa survivor_split.${count}.vcf --export svviz_outputs 1>/home/dnanexus/out/log_files/svviz/svviz.${count}.stdout 2>/home/dnanexus/out/log_files/svviz/svviz.$count.stderr" >> commands.txt
                ((count++))
            done
            
            threads="$(nproc)"
            threads=$((threads / 2))
            parallel --memfree 5G --retries 2 --verbose -a commands.txt eval 2> /dev/null
            
            tar -czf /home/dnanexus/out/"${prefix}".svviz_outputs.tar.gz svviz_outputs/
        fi
    fi
fi

echo "Finishing Parliament2 at time $(date)"
