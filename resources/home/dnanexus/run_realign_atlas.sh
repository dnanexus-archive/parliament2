set -x

input_bam=$1
ref_genome=$2
gatk_jar=$3
prefix=$4
contig=$5

java -Xmx8G -jar "${gatk_jar}" -T IndelRealigner -R "${ref_genome}" -I "${input_bam}" -targetIntervals realign.intervals -L "${contig}" -known Homo_sapiens_assembly38.dbsnp138.vcf.gz -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz -o indel_realigned."${contig}".bam 1> /home/dnanexus/out/log_files/indel_realigner.${contig}.stdout.log 2> /home/dnanexus/out/log_files/indel_realigner.${contig}.stderr.log

xatlas --ref "${ref_genome}" --in indel_realigned."${contig}".bam --prefix "${prefix}.${contig}" -s "${prefix}.${contig}" --gvcf 1> /home/dnanexus/out/log_files/xatlas.${contig}.stdout.log 2> /home/dnanexus/out/log_files/xatlas.${contig}.stderr.log

rm indel_realigned."${contig}".bam