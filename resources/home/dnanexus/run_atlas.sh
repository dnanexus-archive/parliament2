

set -x

job_number=$1
prefix=$2
chromosome=$3
ref_prefix=$4
sample=$5

region_cmd=$(tail -n 1 atlas_commands_$job_number)

./xatlas --ref ${ref_prefix}.fa --in input.$job_number.bam --prefix ${chromosome}_${job_number} -s ${sample} ${region_cmd} --gvcf 1>atlas.$i.stdout 2>atlas.$i.stderr
job_status=$?
tries=0
while [ $job_status -ge 1 ]; do
    rm ${chromosome}_${job_number}_snp.vcf
    rm ${chromosome}_${job_number}_indel.vcf
    ./xatlas --ref ${ref_prefix}.fa --in input.$job_number.bam --prefix ${chromosome}_${job_number} -s ${sample} ${region_cmd} --gvcf 1>atlas.$i.stdout 2>atlas.$i.stderr
    job_status=$?
    echo "Rerunning $chromosome, try $tries" >> failure_report
    tries=$(expr $tries + 1)
    if [ $tries -ge 8 ]; then
	dx-jobutil-report-error "Atlas expended its reruns on chromosome $chromosome, attempted $tries times"
    fi
done

python filter_ref_blocks.py ${chromosome}_${job_number}_snp.vcf $chromosome > ${chromosome}_${job_number}_snp.filtered.vcf
mv ${chromosome}_${job_number}_snp.filtered.vcf ${chromosome}_${job_number}_snp.vcf
python filter_ref_blocks.py ${chromosome}_${job_number}_indel.vcf $chromosome > ${chromosome}_${job_number}_indel.filtered.vcf
mv ${chromosome}_${job_number}_indel.filtered.vcf ${chromosome}_${job_number}_indel.vcf