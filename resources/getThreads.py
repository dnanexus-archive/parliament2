import sys

# active_threads=`python /getThreads.py "$breakdancer_processes" "$cnvnator_processes" "$sambamba_processes" "$manta_processes" "$breakseq_processes" "$delly_processes" "$lumpy_processes" "$atlas_processes" "$indel_realigner_processes"`

breakdancer_threads = int(sys.argv[1])
cnvnator_threads = int(sys.argv[2])
sambamba_threads = int(sys.argv[3])
manta_processes = int(sys.argv[4])
breakseq_processes = int(sys.argv[5])
delly_processes = int(sys.argv[6])
lumpy_processes = int(sys.argv[7])
atlas_processes = int(sys.argv[8])
realign_processes = int(sys.argv[9])

total_threads = breakdancer_threads + cnvnator_threads + int( (0.25 * float(sambamba_threads) ) ) + (8 * manta_processes) + (0 * breakseq_processes) + delly_processes + lumpy_processes + atlas_processes + realign_processes

if total_threads < 1:
    print 1
else:
    print int(total_threads)
