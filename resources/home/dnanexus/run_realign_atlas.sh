input_bam=$1
ref_genome=$2
gatk_jar=$3
prefix=$4
contig=$5

echo "Running RealignerTargetCreator for contig $contig"
java -Xmx8G -jar "${gatk_jar}" -T RealignerTargetCreator -R ref.fa -I input.bam -o realign."${contig}".intervals -L "${contig}" -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz 1> /home/dnanexus/out/log_files/realigner_target_creator/"${prefix}".realigner_target_creator."${contig}".stdout.log 2> /home/dnanexus/out/log_files/realigner_target_creator/"${prefix}".realigner_target_creator."${contig}".stderr.log

echo "Running IndelRealigner for contig $contig"
java -Xmx8G -jar "${gatk_jar}" -T IndelRealigner -R "${ref_genome}" -I "${input_bam}" -targetIntervals realign."${contig}".intervals -L "${contig}" -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz -o indel_realigned."${contig}".bam 1> /home/dnanexus/out/log_files/indel_realigner/"${prefix}".indel_realigner."${contig}".stdout.log 2> /home/dnanexus/out/log_files/indel_realigner/"${prefix}".indel_realigner."${contig}".stderr.log

sambamba index -t $(nproc) indel_realigned."${contig}".bam

echo "Running xAtlas for contig $contig"
xatlas --ref "${ref_genome}" --in indel_realigned."${contig}".bam --prefix "${prefix}.${contig}" -s "${prefix}.${contig}" --gvcf --enable-strand-filter 1> /home/dnanexus/out/log_files/xatlas/"${prefix}".xatlas."${contig}".stdout.log 2> /home/dnanexus/out/log_files/xatlas/"${prefix}".xatlas.${contig}.stderr.log

rm realign."${contig}".intervals
rm indel_realigned."${contig}".bam
rm indel_realigned."${contig}".bam.bai
