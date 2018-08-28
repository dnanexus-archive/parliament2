set -x

prefix=$1


java -Xmx8G -jar GenomeAnalysisTK.jar -nt 4 -T RealignerTargetCreator -R ref.fa -I input.bam -o realign.intervals -known Homo_sapiens_assembly38.dbsnp138.vcf.gz -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz

java -Xmx8G -jar GenomeAnalysisTK.jar -T IndelRealigner -R ref.fa -I input.bam -targetIntervals realign.intervals -L chr1 -L chr2 -L chr3 -L chr4 -L chr5 -L chr6 -L chr 7 -L chr8 -L chr9 -L chr10 -L chr11 -L chr12 -L chr13 -L chr14 -L chr15 -L chr16 -L chr17 -L chr18 -L chr19 -L chr20 -L chr21 -L chr22 -L chrX -L chrY -L chrM -known Homo_sapiens_assembly38.dbsnp138.vcf.gz -known Homo_sapiens_assembly38.known_indels.vcf.gz -known Mills_and_1000G_gold_standard.indels.hg38.vcf.gz

./xatlas --ref ref.fa --in realigned.bam --prefix ${prefix} -s ${prefix} --gvcf