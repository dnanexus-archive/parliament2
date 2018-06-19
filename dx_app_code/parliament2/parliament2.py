#!/usr/bin/env python

import dxpy
import subprocess
import os.path
import glob

@dxpy.entry_point('main')
def main(**job_inputs):
    # Preparation
    sv_caller_results = []
    
    if 'illumina_bai' in job_inputs:
        illumina_bai = job_inputs['illumina_bai']

    if 'prefix' not in job_inputs:
        bam_name = dxpy.describe(job_inputs['illumina_bam'])['name']
        if bam_name.endswith("cram"):
            prefix = bam_name[:-5]
        else:
            prefix = bam_name[:-4]

    # Running Docker image
    subprocess.check_call(['mkdir', '-p', '/home/dnanexus/in', '/home/dnanexus/out'])

    print "Starting Docker"

    input_bam = dxpy.open_dxfile(job_inputs['illumina_bam'])
    bam_name = "/home/dnanexus/in/{0}".format(input_bam.name)
    dxpy.download_dxfile(input_bam, bam_name)
    
    ref_genome = dxpy.open_dxfile(job_inputs['ref_fasta'])
    ref_name = "/home/dnanexus/in/{0}".format(ref_genome.name)
    dxpy.download_dxfile(ref_genome, ref_name)

    docker_call = ['dx-docker', 'run', '-v', '/home/dnanexus/in/:/home/dnanexus/in/', '-v', '/home/dnanexus/out/:/home/dnanexus/out/','parliament2:0.0.1', '--bam', bam_name, '-r', ref_name, '--prefix', prefix ]

    if 'illumina_bai' in job_inputs:
        input_bai = dxpy.open_dxfile(job_inputs['illumina_bai'])
        bai_name = "/home/dnanexus/in/{0}".format(input_bai.name)
        dxpy.download_dxfile(input_bai, bai_name)

        docker_call.extend(['--bai', bai_name])

    if job_inputs['filter_short_contigs']:
        docker_call.append('--filter_short_contigs')
    if job_inputs['run_breakdancer']:
        docker_call.append('--breakdancer')
    if job_inputs['run_breakseq']:
        docker_call.append('--breakseq')
    if job_inputs['run_manta']:
        docker_call.append('--manta')
    if job_inputs['run_cnvnator']:
        docker_call.append('--cnvnator')
    if job_inputs['run_lumpy']:
        docker_call.append('--lumpy')
    if job_inputs['run_delly_inversion']:
        docker_call.append('--delly_inversion')
    if job_inputs['run_delly_insertion']:
        docker_call.append('--delly_insertion')
    if job_inputs['run_delly_deletion']:
        docker_call.append('--delly_deletion')
    if job_inputs['run_delly_duplication']:
        docker_call.append('--delly_duplication')
    if job_inputs['run_genotype_candidates']:
        docker_call.append('--genotype')
    if job_inputs['run_svviz']:
        docker_call.append('--svviz')
    if job_inputs['svviz_only_validated_candidates']:
        docker_call.append('--svviz_only_validated_candidates')

    subprocess.check_call(docker_call)

    print "Docker image finished"

    print "Subjob finishing..."

    sv_caller_results_names = glob.glob('/home/dnanexus/out/sv_caller_results/*')
    sv_caller_results_upload = []
    for f in sv_caller_results_names:
        sv_caller_results_upload.append(dxpy.dxlink(dxpy.upload_local_file(f)))

    output = {
        'sv_caller_results' : sv_caller_results_upload,
    }

    if job_inputs['run_genotype_candidates']:
        svtyped_vcf_names = glob.glob('/home/dnanexus/out/svtyped_vcfs/*')
        svtyped_vcfs_upload = []
        for f in svtyped_vcf_names:
            svtyped_vcfs_upload.append(dxpy.dxlink(dxpy.upload_local_file(f)))

        output['svtyped_vcfs'] = svtyped_vcfs_upload
        output['combined_genotypes'] = dxpy.dxlink(dxpy.upload_local_file('/home/dnanexus/out/{0}.combined.genotyped.vcf'.format(prefix)))
        
    if job_inputs['run_svviz'] and os.path.isfile('/home/dnanexus/out/{0}.svviz_outputs.tar.gz'.format(prefix)):
        output['svviz_outputs'] = dxpy.dxlink(dxpy.upload_local_file('/home/dnanexus/out/{0}.svviz_outputs.tar.gz'.format(prefix)))

    return output

dxpy.run()
