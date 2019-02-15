#!/bin/bash

input=$1
directory=$2
output=$3
input_bam=$4

input_lines=$(grep -v \# $input | wc -l)
threads=$(nproc)
threads=$(expr $threads \* 4)
if [[ $input_lines -ge $threads ]]; then
    lines=$(expr $input_lines / $threads)
    split -d -a 5 -l $lines $input $directory
fi

i=0
for item in $directory*; do
    i=$(expr $i + 1)
    grep \# $input > $directory/$i
    grep -v \# $item >> $directory/$i
    echo "svtyper -B $input_bam -i $directory/$i >> $directory/$i" >> $output.cmds
done

# We don't have the memfree option is the Ubuntu 14.04 version  of parallel
#parallel --memfree 5G --retries 2 --verbose -a $output.cmds eval 2> /dev/null
parallel --retries 2 --verbose -a $output.cmds eval 2> /dev/null

grep \# $input > $output
for item in $directory/*; do
    grep -v \# $item >> $output
done
