illumina_bam=$1
illumina_bai=$2
ref_fasta=$3
prefix=$4
rerun_chromosomes=$5
filter_short_contigs=$6
run_breakdancer=$7
run_breakseq=$8
run_manta=$9
run_cnvnator=${10}
run_lumpy=${11}
run_delly_deletion=${12}
run_delly_insertion=${13}
run_delly_inversion=${14}
run_delly_duplication=${15}
run_genotype_candidates=${16}
run_svviz=${17}
svviz_only_validated_candidates=${18}
dnanexus=${19}

cp "${ref_fasta}" ref.fa

echo "Classify FASTA"

samtools faidx ref.fa &
ref_genome=$(python /home/dnanexus/get_reference.py)
lumpy_exclude_string=""
if [[ "$ref_genome" == "b37" ]]; then
    lumpy_exclude_string="-x b37.bed"
elif [[ "$ref_genome" == "hg19" ]]; then
    lumpy_exclude_string="-x hg19.bed"
else
    lumpy_exclude_string="-x hg38.bed"
fi

lumpy_scripts="/home/dnanexus/lumpy-sv/scripts"

# Get extension and threads
extn=${illumina_bam##*.}
threads="$(nproc)"
threads=$((threads - 3))

echo "Set up and index BAM/CRAM"

# # Allow for CRAM files
if [[ "$extn" == "cram" ]] || [[ "$extn" == "CRAM" ]]; then
    echo "CRAM file input"
    mkfifo tmp_input.bam
    samtools view "${illumina_bam}" -bh -@ "$threads" -T ref.fa -o - | tee tmp_input.bam > input.bam & 
    samtools index tmp_input.bam
    wait
    cp tmp_input.bam.bai input.bam.bai
    rm tmp_input.bam
elif [[ "$illumina_bai" == "None" ]]; then
    echo "BAM file input, no index exists"
    cp "${illumina_bam}" input.bam
    samtools index input.bam
else
    echo "BAM file input, index exists"
    cp "${illumina_bam}" input.bam
    cp "${illumina_bai}" input.bam.bai
fi

wait

echo "Generate contigs"

samtools view -H input.bam | python /getContigs.py "$filter_short_contigs" > contigs

# See which chromosomes are in the BAM file
samtools idxstats input.bam | cut -f 1 | uniq > bam_chromosomes.txt &

mkdir -p /home/dnanexus/out/log_files/

if [[ "$run_breakseq" == "True" || "$run_manta" == "True" ]]; then
    echo "Launching jobs that cannot be parallelized by contig"
fi

# JOBS THAT CANNOT BE PARALLELIZED BY CONTIG
# BREAKSEQ2
if [[ "$run_breakseq" == "True" ]]; then
    echo "BreakSeq"
    bplib="/breakseq2_bplib_20150129/breakseq2_bplib_20150129.gff"
    work="breakseq2"
    timeout 6h ./breakseq2-2.2/scripts/run_breakseq2.py --reference ref.fa \
        --bams input.bam --work "$work" \
        --bwa /usr/local/bin/bwa --samtools /usr/local/bin/samtools \
        --bplib_gff "$bplib" \
        --nthreads "$(nproc)" --bplib_gff "$bplib" \
        --sample "$prefix" 1> /home/dnanexus/out/log_files/breakseq.stdout.log 2> /home/dnanexus/out/log_files/breakseq.stderr.log &
fi

# MANTA
if [[ "$run_manta" == "True" ]]; then
    echo "Manta"
    timeout 6h runManta 1> /home/dnanexus/out/log_files/manta.stdout.log 2> /home/dnanexus/out/log_files/manta.stderr.log &
fi

# PREPARE FOR BREAKDANCER
if [[ "$run_breakdancer" == "True" ]]; then
    timeout 2h /breakdancer/cpp/bam2cfg -o breakdancer.cfg input.bam
fi

concat_breakdancer_cmd=""
concat_cnvnator_cmd=""
delly_deletion_concat=""
delly_inversion_concat=""
delly_duplication_concat=""
delly_insertion_concat=""
lumpy_merge_command=""

if [[ "$run_delly_deletion" == "True" ]] || [[ "$run_delly_insertion" == "True" ]] || [[ "$run_delly_inversion" == "True" ]] || [[ "$run_delly_duplication" == "True" ]]; then
   run_delly="True"
fi

count=0
# Process management for launching jobs
if [[ "$run_cnvnator" == "True" ]] || [[ "$run_delly" == "True" ]] || [[ "$run_breakdancer" == "True" ]] || [[ "$run_lumpy" == "True" ]]; then
    echo "Launching jobs parallelized by contig"
    while read contig; do
        if [[ $(samtools view input.bam "$contig" | head -n 20 | wc -l) -ge 10 ]]; then
            if [[ "$run_breakdancer" == "True" ]]; then
                echo "Running Breakdancer for contig $contig"
                timeout 4h /breakdancer/cpp/breakdancer-max breakdancer.cfg input.bam -o "$contig" > breakdancer-"$count".ctx &
                concat_breakdancer_cmd="$concat_breakdancer_cmd breakdancer-$count.ctx"
            fi

            if [[ "$run_cnvnator" == "True" ]]; then
                echo "Running CNVnator for contig $contig"
                runCNVnator "$contig" "$count" &
                concat_cnvnator_cmd="$concat_cnvnator_cmd output.cnvnator_calls-$count"
            fi

            echo "Running sambamba view"
            timeout 2h sambamba view -h -f bam -t $(nproc) input.bam $contig > chr.$count.bam
            echo "Running sambamba index"
            sambamba index -t $(nproc) chr.$count.bam 

            if [[ "$run_delly_deletion" == "True" ]]; then  
                echo "Running Delly (deletions) for contig $contig"
                timeout 6h delly -t DEL -o $count.delly.deletion.vcf -g ref.fa chr.$count.bam & 
                delly_deletion_concat="$delly_deletion_concat $count.delly.deletion.vcf"
            fi

            if [[ "$run_delly_inversion" == "True" ]]; then 
                echo "Running Delly (inversions) for contig $contig"
                timeout 6h delly -t INV -o $count.delly.inversion.vcf -g ref.fa chr.$count.bam &
                delly_inversion_concat="$delly_inversion_concat $count.delly.inversion.vcf"
            fi

            if [[ "$run_delly_duplication" == "True" ]]; then 
                echo "Running Delly (duplications) for contig $contig"
                timeout 6h delly -t DUP -o $count.delly.duplication.vcf -g ref.fa chr.$count.bam &
                delly_duplication_concat="$delly_duplication_concat $count.delly.duplication.vcf"
            fi

            if [[ "$run_delly_insertion" == "True" ]]; then 
                echo "Running Delly (insertions) for contig $contig"
                timeout 6h delly -t INS -o $count.delly.insertion.vcf -g ref.fa chr.$count.bam &
                delly_insertion_concat="$delly_insertion_concat $count.delly.insertion.vcf"
            fi
            
            if [[ "$run_lumpy" == "True" ]]; then
                echo "Running Lumpy for contig $contig"
                timeout 6h ./lumpy-sv/bin/lumpyexpress -B chr.$count.bam -o lumpy.$count.vcf $lumpy_exclude_string -k &
                lumpy_merge_command="$lumpy_merge_command lumpy.$count.vcf"
            fi

            breakdancer_threads=$(top -n 1 -b -d 10 | grep -c breakdancer)
            cnvnator_threads=$(top -n 1 -b -d 10 | grep -c cnvnator)
            sambamba_processes=$(top -n 1 -b -d 10 | grep -c sambamba)
            manta_processes=$(top -n 1 -b -d 10 | grep -c manta)
            breakseq_processes=$(top -n 1 -b -d 10 | grep -c breakseq)
            delly_processes=$(top -n 1 -b -d 10 | grep -c delly)
            lumpy_processes=$(top -n 1 -b -d 10 | grep -c lumpy)
            active_threads=$(python /getThreads.py "$breakdancer_threads" "$cnvnator_threads" "$sambamba_processes" "$manta_processes" "$breakseq_processes" "$delly_processes" "$lumpy_processes")
            
            while [[ $active_threads -ge $(nproc) ]]; do
                echo "Waiting for 60 seconds"
                breakdancer_threads=$(top -n 1 -b -d 10 | grep -c breakdancer)
                cnvnator_threads=$(top -n 1 -b -d 10 | grep -c cnvnator)
                sambamba_processes=$(top -n 1 -b -d 10 | grep -c sambamba)
                manta_processes=$(top -n 1 -b -d 10 | grep -c manta)
                breakseq_processes=$(top -n 1 -b -d 10 | grep -c breakseq)
                delly_processes=$(top -n 1 -b -d 10 | grep -c delly)
                lumpy_processes=$(top -n 1 -b -d 10 | grep -c lumpy)
                active_threads=$(python /getThreads.py "$breakdancer_threads" "$cnvnator_threads" "$sambamba_processes" "$manta_processes" "$breakseq_processes" "$delly_processes" "$lumpy_processes")
                sleep 60
            done
            count=$((count + 1))
        fi
    done < contigs
fi

wait
# Only install SVTyper if necessary
if [[ "$run_genotype_candidates" == "True" ]]; then
    pip install git+https://github.com/hall-lab/svtyper.git -q &
fi

echo "Converting results to VCF format"
mkdir -p /home/dnanexus/out/sv_caller_results/
mkdir -p /home/dnanexus/tmp/

(if [[ "$run_breakdancer" == "True" ]] && [[ -n "$concat_breakdancer_cmd" ]]; then
    echo "Convert Breakdancer results to VCF format"
    # cat contents of each file into output file: lack of quotes intentional
    cat $concat_breakdancer_cmd > breakdancer.output

    cp breakdancer.output /home/dnanexus/out/sv_caller_results/"$prefix".breakdancer.ctx

    python /BreakDancer2Merge.py 1.0 breakdancer.output "$prefix"

    python /convert_breakdancer_vcf.py < breakdancer.output > breakdancer.vcf
    cp breakdancer.vcf /home/dnanexus/out/sv_caller_results/"$prefix".breakdancer.vcf
fi) &

(if [[ "$run_breakseq" == "True" ]]; then
    echo "Convert Breakseq results to VCF format"
    cd "$work" || return
    find ./*.log | tar -zcvf log.tar.gz -T -
    rm -rf ./*.log
    cd /home/dnanexus || return

    mv breakseq2/breakseq.vcf.gz .
    gunzip breakseq.vcf.gz

    cp breakseq2/breakseq_genotyped.gff /home/dnanexus/out/sv_caller_results/"$prefix".breakseq.gff
    cp breakseq.vcf /home/dnanexus/out/sv_caller_results/"$prefix".breakseq.vcf
    cp breakseq2/final.bam /home/dnanexus/out/sv_caller_results/"$prefix".breakseq.bam
fi) &

(if [[ "$run_cnvnator" == "True" ]] && [[ -n "$concat_cnvnator_cmd" ]]; then
    echo "Convert CNVnator results to VCF format"
    # cat contents of each file into output file: lack of quotes intentional
    cat $concat_cnvnator_cmd > cnvnator.output

    perl /usr/utils/cnvnator2VCF.pl cnvnator.output > cnvnator.vcf

    cp cnvnator.vcf /home/dnanexus/out/sv_caller_results/"$prefix".cnvnator.vcf
    cp cnvnator.output /home/dnanexus/out/sv_caller_results/"$prefix".cnvnator.output
fi) &

(if [[ "$run_delly_deletion" == "True" ]]; then 
    echo "Convert Delly deletion results to VCF format"
    python /convertHeader.py "$prefix" "$delly_deletion_concat" | vcf-sort -c | uniq > tmp/delly.deletion.vcf
    rm *delly.deletion.vcf

    cp tmp/delly.deletion.vcf delly.deletion.vcf
    cp delly.deletion.vcf /home/dnanexus/out/sv_caller_results/"$prefix".delly.deletion.vcf
fi) &

(if [[ "$run_delly_duplication" == "True" ]]; then
    echo "Convert Delly duplication results to VCF format"
    python /convertHeader.py "$prefix" "$delly_duplication_concat" | vcf-sort -c | uniq > tmp/delly.duplication.vcf
    rm *delly.duplication.vcf

    cp tmp/delly.duplication.vcf delly.duplication.vcf
    cp delly.duplication.vcf /home/dnanexus/out/sv_caller_results/"$prefix".delly.duplication.vcf
fi) &

(if [[ "$run_delly_insertion" == "True" ]]; then
    echo "Convert Delly insertion results to VCF format"
    python /convertHeader.py "$prefix" "$delly_insertion_concat" | vcf-sort -c | uniq > tmp/delly.insertion.vcf
    rm *delly.insertion.vcf

    cp tmp/delly.insertion.vcf delly.insertion.vcf
    cp delly.insertion.vcf /home/dnanexus/out/sv_caller_results/"$prefix".delly.insertion.vcf
fi) &

(if [[ "$run_delly_inversion" == "True" ]]; then
    echo "Convert Delly inversion results to VCF format"
    python /convertHeader.py "$prefix" "$delly_inversion_concat" | vcf-sort -c | uniq > tmp/delly.inversion.vcf
    rm *delly.inversion.vcf

    cp tmp/delly.inversion.vcf delly.inversion.vcf
    cp delly.inversion.vcf /home/dnanexus/out/sv_caller_results/"$prefix".delly.inversion.vcf
fi) &

(if [[ "$run_lumpy" == "True" ]]; then
    echo "Convert Lumpy results to VCF format"
    python /convertHeader.py "$prefix" "$lumpy_merge_command" | vcf-sort -c | uniq > tmp/lumpy.vcf
    rm lumpy*vcf

    cp tmp/lumpy.vcf lumpy.vcf
    cp lumpy.vcf /home/dnanexus/out/sv_caller_results/"$prefix".lumpy.vcf
fi) &

(if [[ "$run_manta" == "True" ]]; then
    echo "Convert Manta results to VCF format"
    cp manta/results/variants/diploidSV.vcf.gz /home/dnanexus/out/sv_caller_results/"$prefix".manta.diploidSV.vcf.gz
    cp manta/results/stats/alignmentStatsSummary.txt /home/dnanexus/out/sv_caller_results/"$prefix".manta.alignmentStatsSummary.txt

    mv manta/results/variants/diploidSV.vcf.gz .
    gunzip diploidSV.vcf.gz
    python /Manta2merge.py 1.0 diploidSV.vcf "$prefix"
fi) &

wait

set -e
# Verify that there are VCF files available
if [[ -z $(find . -name "*.vcf") ]]; then
    if [[ "$dnanexus" == "True" ]]; then
        dx-jobutil-report-error "ERROR: SVTyper requested, but candidate VCF files required to genotype. No VCF files found."
    else
        echo "ERROR: SVTyper requested, but candidate VCF files required to genotype. No VCF files found."
        exit 1
    fi
fi
set +e

if [[ "$rerun_chromosomes" == "True" ]]; then
    # Check that all VCF files have all chromosomes
    echo "Verify that all chromosomes have been successfully analyzed"

    concat_breakdancer_cmd=""
    concat_cnvnator_cmd=""
    delly_deletion_concat=""
    delly_inversion_concat=""
    delly_duplication_concat=""
    delly_insertion_concat=""
    lumpy_merge_command=""
    count=0
    # Chromosome dropping expected to be rare; process management less complicated
    for item in *.vcf; do
        cat "${item}" | cut -f 1 | grep -v "#" | uniq > "${item%.vcf}"_chromosomes.txt
        python ./verify_chromosomes.py "${item%.vcf}"_chromosomes.txt > contigs

        if [[ -z "$contigs" ]]; then
            echo "No chromosomes to re-run for ${item}"
        else
            echo "Re-running for file ${item}"
            if [[ "${item}" = *"breakdancer"* ]]; then
                while read contig; do
                    echo "Re-running Breakdancer for contig $contig"
                    timeout 4h /breakdancer/cpp/breakdancer-max breakdancer.cfg input.bam -o "$contig" > breakdancer-"$count".ctx &
                    concat_breakdancer_cmd="$concat_breakdancer_cmd breakdancer-$count.ctx"
                done < contigs
            elif [[ "${item}" = *"cnvnator"* ]]; then
                while read contig; do
                    echo "Re-running CNVnator for contig $contig"
                    runCNVnator "$contig" "$count" &
                    concat_cnvnator_cmd="$concat_cnvnator_cmd output.cnvnator_calls-$count"
                done < contigs
            elif [[ "${item}" = *"delly.inversion"* ]] || [[ "${item}" = *"delly.inversion"* ]] || [[ "${item}" = *"delly.duplication"* ]] || [[ "${item}" = *"delly.deletion"* ]] || [[ "${item}" = *"lumpy"* ]]; then
                while read contigs; do
                    timeout 2h sambamba view -h -f bam -t $(nproc) input.bam $contig > chr.$count.bam
                    echo "Re-running sambamba index for contig $contig"
                    sambamba index -t $(nproc) chr.$count.bam        
                done < contigs
            fi

            if [[ "${item}" = *"delly.deletion"* ]]; then
                while read contig; do
                    echo "Re-running Delly (deletions) for contig $contig"
                    timeout 6h delly -t DEL -o $count.delly.deletion.vcf -g ref.fa chr.$count.bam & 
                    delly_deletion_concat="$delly_deletion_concat $count.delly.deletion.vcf"
                done < contigs
            elif [[ "${item}" = *"delly.duplication"* ]]; then
                while read contig; do
                    echo "Re-running Delly (duplications) for contig $contig"
                    timeout 6h delly -t DUP -o $count.delly.duplication.vcf -g ref.fa chr.$count.bam &
                    delly_duplication_concat="$delly_duplication_concat $count.delly.duplication.vcf"
                done < contigs
            elif [[ "${item}" = *"delly.insertion"* ]]; then
                while read contig; do
                    echo "Re-running Delly (insertions) for contig $contig"
                    timeout 6h delly -t INS -o $count.delly.insertion.vcf -g ref.fa chr.$count.bam &
                    delly_insertion_concat="$delly_insertion_concat $count.delly.insertion.vcf"
                done < contigs
            elif [[ "${item}" = *"delly.inversion"* ]]; then
                while read contig; do
                    echo "Re-running Delly (inversions) for contig $contig"
                    timeout 6h delly -t INV -o $count.delly.inversion.vcf -g ref.fa chr.$count.bam &
                    delly_inversion_concat="$delly_inversion_concat $count.delly.inversion.vcf"
                done < contigs
            elif [[ "${item}" = *"lumpy"* ]]; then
                while read contig; do
                    echo "Re-running Lumpy for contig $contig"
                    timeout 6h ./lumpy-sv/bin/lumpyexpress -B chr.$count.bam -o lumpy.$count.vcf $lumpy_exclude_string -k &
                    lumpy_merge_command="$lumpy_merge_command lumpy.$count.vcf"
                done < contigs
            fi

            wait

            # Converting dropped chromosomes to VCF format
            caller=""
            if [[ "${item}" = *"breakdancer"* ]]; then
                caller="breakdancer"
                echo "Converting Breakdancer re-run results to VCF format"
                # cat contents of each file into output file: lack of quotes intentional
                cat $concat_breakdancer_cmd > breakdancer.output

                cp breakdancer.output /home/dnanexus/out/sv_caller_results/"$prefix".breakdancer.ctx

                python /BreakDancer2Merge.py 1.0 breakdancer.output "$prefix"

                python /convert_breakdancer_vcf.py < breakdancer.output > "$prefix".breakdancer.vcf

            elif [[ "${item}" = *"cnvnator"* ]]; then
                caller="cnvnator"
                echo "Convert CNVnator re-run results to VCF format"
                # cat contents of each file into output file: lack of quotes intentional
                cat $concat_cnvnator_cmd > cnvnator.output

                perl /usr/utils/cnvnator2VCF.pl cnvnator.output > cnvnator.vcf

                cp cnvnator.output "$prefix"_rerun.cnvnator.output
                mv /home/dnanexus/out/sv_caller_results/"$prefix".cnvnator.output "$prefix"_original.cnvnator.output
                cat "$prefix"_rerun.cnvnator.output "$prefix"_original.cnvnator.output > /home/dnanexus/out/sv_caller_results/"$prefix".cnvnator.output

            elif [[ "${item}" = *"delly.deletion"* ]]; then
                caller="delly.deletion"
                echo "Convert Delly deletion re-run results to VCF format"
                python /convertHeader.py "$prefix" "$delly_deletion_concat" | vcf-sort -c | uniq > delly.deletion.vcf

            elif [[ "${item}" = *"delly.duplication"* ]]; then
                caller="delly.duplication"
                echo "Convert Delly duplication re-runresults to VCF format"
                python /convertHeader.py "$prefix" "$delly_duplication_concat" | vcf-sort -c | uniq > delly.duplication.vcf

            elif [[ "${item}" = *"delly.insertion"* ]]; then
                caller="delly.insertion"
                echo "Convert Delly insertion results to VCF format"
                python /convertHeader.py "$prefix" "$delly_insertion_concat" | vcf-sort -c | uniq > delly.insertion.vcf

            elif [[ "${item}" = *"delly.inversion"* ]]; then
                caller="delly.inversion"
                echo "Convert Delly inversion results to VCF format"
                python /convertHeader.py "$prefix" "$delly_inversion_concat" | vcf-sort -c | uniq > delly.inversion.vcf

            elif [[ "${item}" = *"lumpy"* ]]; then
                caller="lumpy"
                echo "Convert Lumpy re-run results to VCF format"
                python /convertHeader.py "$prefix" "$lumpy_merge_command" | vcf-sort -c | uniq > lumpy.vcf

            fi
            if [[ -n "$caller" ]]; then
                cp "$caller".vcf "$prefix"_rerun."$caller".vcf

                mv /home/dnanexus/out/sv_caller_results/"$prefix"."$caller".vcf "$prefix"_original."$caller".vcf
                vcf-concat "$prefix"_rerun."$caller".vcf "$prefix"_original."$caller".vcf > "$prefix"_unsorted."$caller".vcf
                vcf-sort -c "$prefix"_unsorted.breakdancer.vcf > /home/dnanexus/out/sv_caller_results/"$prefix"."$caller".vcf
            fi
        fi
    done
fi

# Run SVtyper and SVviz
if [[ "$run_genotype_candidates" == "True" ]]; then
    echo "Running SVTyper"
    # SVviz and BreakSeq have mutually exclusive versions of pysam required, so
    # SVviz is only installed later and if necessary
    if [[ "$run_svviz" == "True" ]]; then
        pip install svviz -q &
    fi

    mkdir -p /home/dnanexus/out/svtyped_vcfs/

    i=0
    # Breakdancer
    if [[ "$run_breakdancer" == "True" ]]; then
        echo "Running SVTyper on Breakdancer outputs"
        svtyper-sso --core $(nproc) -i /home/dnanexus/breakdancer.vcf -B input.bam > /home/dnanexus/"${prefix}".breakdancer.svtyped.vcf
        # mkdir /home/dnanexus/svtype_breakdancer
        # bash ./parallelize_svtyper.sh /home/dnanexus/breakdancer.vcf svtype_breakdancer /home/dnanexus/"${prefix}".breakdancer.svtyped.vcf input.bam
    fi

    # Breakseq
    if [[ "$run_breakseq" == "True" ]]; then
        echo "Running SVTyper on BreakSeq outputs"
        # svtyper-sso --core $(nproc) -i /home/dnanexus/breakseq.vcf -B input.bam > /home/dnanexus/"${prefix}".breakseq.svtyped.vcf

        mkdir /home/dnanexus/svtype_breakseq
        bash ./parallelize_svtyper.sh /home/dnanexus/breakseq.vcf svtype_breakseq /home/dnanexus/"${prefix}".breakseq.svtyped.vcf input.bam

        if [[ -f breakseq.vcf ]]; then
            echo breakseq.vcf >> survivor_inputs
        fi
    fi

    # CNVnator
    if [[ "$run_cnvnator" == "True" ]]; then
        echo "Running SVTyper on CNVnator outputs"
        # svtyper-sso --core $(nproc) -i /home/dnanexus/cnvnator.vcf -B input.bam > /home/dnanexus/"${prefix}".cnvnator.svtyped.vcf
        mkdir /home/dnanexus/svtype_cnvnator
        cat cnvnator.vcf | python /get_uncalled_cnvnator.py | python /add_ciend.py 1000 > /home/dnanexus/cnvnator.ci.vcf
        timeout -k 500 60m bash ./parallelize_svtyper.sh /home/dnanexus/cnvnator.vcf svtype_cnvnator "${prefix}".cnvnator.svtyped.vcf input.bam
    fi

    # Delly
    if [[ "$run_delly" == "True" ]]; then
        echo "Running SVTyper on Delly outputs"
        for item in delly*vcf; do
            svtyper-sso --core $(nproc) -i "${item}" -B input.bam > /home/dnanexus/"${prefix}"."${item%.vcf}".svtyped.vcf
        done
    fi

    # Lumpy
    if [[ "$run_lumpy" == "True" ]]; then
        echo "Running SVTyper on Lumpy outputs"
        svtyper-sso --core $(nproc) -i /home/dnanexus/lumpy.vcf -B input.bam > /home/dnanexus/"${prefix}".lumpy.svtyped.vcf
    fi

    # Manta
    if [[ "$run_manta" == "True" ]]; then
        if [[ -f diploidSV.vcf ]]; then
            mv diploidSV.vcf /home/dnanexus/"${prefix}".manta.svtyped.vcf
            echo /home/dnanexus/"${prefix}".manta.svtyped.vcf >> survivor_inputs
        fi
    fi

    # Prepare inputs for SURVIVOR
    echo "Preparing inputs for SURVIVOR"
    for item in *svtyped.vcf; do
        python /adjust_svtyper_genotypes.py "$item" > adjusted.vcf
        mv adjusted.vcf "${item}"
        echo "${item}" >> survivor_inputs
    done

    # Prepare SVtyped VCFs for upload
    for item in *svtyped.vcf; do
        cp "$item" /home/dnanexus/out/svtyped_vcfs/$item
    done

    # Run SURVIVOR
    echo "Running SURVIVOR"
    survivor 5 survivor_inputs 200 1 1 0 0 10 survivor.output.vcf

    # Prepare SURVIVOR outputs for upload
    cat survivor.output.vcf | vcf-sort -c > survivor_sorted.vcf
    python /combine_combined.py survivor_sorted.vcf "$prefix" | python /correct_max_position.py > /home/dnanexus/out/"$prefix".combined.genotyped.vcf

    wait

    # Run svviz
    if [[ "$run_svviz" == "True" ]]; then
        echo "Running svviz"
        mkdir svviz_outputs

        grep \# survivor_sorted.vcf > header.txt

        if [[ "$svviz_only_validated_candidates" == "True" ]]; then
            echo "Only visualizing validated candidates"
            grep -v \# survivor_sorted.vcf | grep -E -h "0/1|1/1" > vcf_entries.vcf
        else
            grep -v \# survivor_sorted.vcf > vcf_entries.vcf
        fi

        NUM_FILES=500
        vcf_entries=$(wc -l < vcf_entries.vcf | tr -d ' ')

        # Verify that there are VCF entries available to visualize
        if [[ $vcf_entries == 0 ]]; then
            # not throwing an error
            echo "No entries in the VCF to visualize. Not running svviz."
        else
            ((lines_per_file = (vcf_entries + NUM_FILES - 1) / NUM_FILES))
            split --lines=${lines_per_file} vcf_entries.vcf small_vcf.
            count=0

            for item in small_vcf*; do
                cat header.txt $item > survivor_split.${count}.vcf
                echo "timeout -k 100 5m svviz --pair-min-mapq 30 --max-deletion-size 5000 --max-reads 10000 --fast --type batch --summary svviz_summary.tsv -b input.bam ref.fa survivor_split.$count.vcf --export svviz_outputs 1>svviz.$count.stdout 2>svviz.$count.stderr" >> commands.txt
                ((count++))
            done
            
            threads=$(nproc)
            threads=$((threads / 4))
            parallel --verbose -j $threads -a commands.txt eval 2> /dev/null
            
            tar -czf /home/dnanexus/out/"$prefix".svviz_outputs.tar.gz svviz_outputs/
        fi
    fi
fi