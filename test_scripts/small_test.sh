#!/usr/bin/env bash

dx login --token $DX_AUTH_TOKEN --noprojects
# Download small input BAM and index
dx download file-By3JP400k0B037Jpv1Jq856f -o small_input.bam
dx download file-Bzp2vG80X3VQv24XgQx0Qy1J -o small_input.bai
# Download reference FASTA and index
dx download file-B6ZY7VG2J35Vfvpkj8y0KZ01 -o ref.fa.gz
dx download file-ByGVY4j04Y0YJ0yJpj0f8qPG -o ref.fa.fai
docker run dnanexus/parliament2:$TAG --bam small_input.bam --ref_genome ref.fa.gz --prefix breakdancer --breakdancer 