input_bam=$1
ref_genome=$2
gatk_jar=$3
prefix=$4
contig=$5

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
    done
}

echo "Running RealignerTargetCreator for contig $contig"
java -Xmx8G -jar "${gatk_jar}" -T RealignerTargetCreator -R ref.fa -I input.bam -o realign."${contig}".intervals -L "${contig}" -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz 1> /home/dnanexus/out/log_files/realigner_target_creator/"${prefix}".realigner_target_creator."${contig}".stdout.log 2> /home/dnanexus/out/log_files/realigner_target_creator/"${prefix}".realigner_target_creator."${contig}".stderr.log

check_threads

echo "Running IndelRealigner for contig $contig"
java -Xmx8G -jar "${gatk_jar}" -T IndelRealigner -R "${ref_genome}" -I "${input_bam}" -targetIntervals realign."${contig}".intervals -L "${contig}" -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz -o indel_realigned."${contig}".bam 1> /home/dnanexus/out/log_files/indel_realigner/"${prefix}".indel_realigner."${contig}".stdout.log 2> /home/dnanexus/out/log_files/indel_realigner/"${prefix}".indel_realigner."${contig}".stderr.log

check_threads

sambamba index indel_realigned."${contig}".bam

check_threads

echo "Running xAtlas for contig $contig"
xatlas --ref "${ref_genome}" --in indel_realigned."${contig}".bam --prefix "${prefix}.${contig}" -s "${prefix}.${contig}" --gvcf --enable-strand-filter 1> /home/dnanexus/out/log_files/xatlas/"${prefix}".xatlas."${contig}".stdout.log 2> /home/dnanexus/out/log_files/xatlas/"${prefix}".xatlas.${contig}.stderr.log

rm realign."${contig}".intervals
rm indel_realigned."${contig}".bam
rm indel_realigned."${contig}".bam.bai
