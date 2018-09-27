task runParliamentTask{
    File inputBAM
    File inputBAI

    File fasta
    File fastaFAI

    Int threads

    String bamBase = basename(inputBAM)
    String baiBase = basename(inputBAI)
    String faBase = basename(fasta)
    String faiBase = basename(fastaFAI)

    command{

        mkdir -p /home/dnanexus/in && \
        ln -s ${inputBAM} /home/dnanexus/in/ && \
        ln -s ${inputBAI} /home/dnanexus/in/ && \
        ln -s ${fasta} /home/dnanexus/in/ && \
        ln -s ${fastaFAI} /home/dnanexus/in/ && \
        parliament2.py --bam ${bamBase} --bai ${baiBase} -r ${faBase} --fai ${faiBase} --threads ${threads}
    }

    runtime{
        docker : "erictdawson/parliament2"
        disks : "local-disk 1000 HDD"
        memory : "62G"
        cpu : "32"
    }
}

workflow ParliamentWF{
    File inputBAM
    File inputBAI

    File fasta
    File fastaFAI

    Int threads

    call runParliamentTask{
        input:
            inputBAM=inputBAM,
            inputBAI=inputBAI,
            fasta=fasta,
            fastaFAI=fastaFAI,
            threads=threads
    }
}
