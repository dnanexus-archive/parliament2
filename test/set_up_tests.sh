#!/usr/bin/env bash

mkdir -p /home/dnanexus/in
mkdir -p /home/dnanexus/out

# Download small input BAM and index
wget https://dl.dnanex.us/F/D/6FX1Jz6bp92b9KFv574Fg306kjkGFK1ybKpG35yp/SRR504516_small.bam -o /home/dnanexus/in/small_input.bam
wget https://dl.dnanex.us/F/D/K695ZppQz1v8Pq6yJKKf0426VYyjkk8g32vgv3kZ/SRR504516_small.bam.bai -o /home/dnanexus/in/small_input.bai
# Download reference FASTA and index
wget https://dl.dnanex.us/F/D/bb37ZbXqjFjZY6Fv0G4GzPGjx5QkYJB8XV6kB5K8/hs37d5.fa.gz -o /home/dnanexus/in/ref.fa.gz
wget https://dl.dnanex.us/F/D/p2qJ1z7gb1ZfFJX3XgPP37325kYKVk06zZp1JPbY/hs37d5.fa.fai -o /home/dnanexus/in/ref.fa.fai
