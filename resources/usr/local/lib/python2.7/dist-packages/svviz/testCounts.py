import numpy
import os
import pandas
import six
import sys
import time
from io import StringIO


from svviz import app

class MockArgs(object):
    def __getattr__(self, attr):
        return None

def run(genome, vcfs, bams, previousSummaryPath):
    timings = {}
    summaries = pandas.DataFrame()
    totalTime = 0

    for vcf in vcfs:
        name = os.path.basename(vcf)
        print(">", name, "<")

        args = []
        args.append("test_script")
        args.append("-t batch")
        args.append("--pair-min-mapq 50")
        args.append(" ".join("-b {}".format(bam) for bam in bams))
        args.append(genome)
        args.append(vcf)

        args = " ".join(args).split()

        print(args)
        t0 = time.time()
        curSummary = app.run(args)
        t1 = time.time()

        timings[name] = t1-t0
        totalTime += t1-t0

        curSummary = pandas.read_table(StringIO(six.text_type(curSummary)))
        summaries = pandas.concat([curSummary, summaries])



    if not os.path.exists(previousSummaryPath) or "-f" in sys.argv:
        print("="*30, "SAVING", "="*30)
        summaries.to_csv(previousSummaryPath, sep="\t")
        print(summaries)
        return (True, "")
    else:
        print("="*30, "COMPARING", "="*30)
        previousSummary = pandas.read_table(previousSummaryPath, index_col=0)

        combined = pandas.merge(previousSummary, summaries, how="outer", 
                                on=["variant", "sample","allele","key"],
                                suffixes=["_prev", "_new"])
        combined = combined.set_index(["variant", "sample","allele","key"])#.fillna(0)

        combined["diff"] = combined["value_new"] - combined["value_prev"]
        diff = combined.loc[~numpy.isclose(combined["diff"], 0), "diff"]

        if diff.shape[0] == 0:
            print("--- same as previous run ---")

            # return [True, "", totalTime]
            return (True, "")
        else:
            print(combined.loc[diff.index])
            return (False, "not equal to previous")



if __name__ == '__main__':
    genome = "/Volumes/frida/nspies/data/hs37d5.fa"
    vcfs = [
        "/Users/nspies/Projects/svviz/tests/na12878_test_deletions.vcf",
        ]
    bams = ["/Volumes/frida/nspies/NA12878/NA12878.mapped.ILLUMINA.bwa.CEU.high_coverage_pcr_free.20130906.bam"]
    previousSummaryPath = "/Users/nspies/Projects/svviz/tests/previousSummary.tsv"

    run(genome, vcfs, bams, previousSummaryPath)