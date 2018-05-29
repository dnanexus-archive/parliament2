import collections
import numpy

class Summary(object):
    def __init__(self):
        self. header = ["variant", "sample","allele", "key","value"]
        self.stats = []

    def addVariantResults(self, dataHub):
        variant = str(dataHub.variant)
        for sampleName, sample in dataHub.samples.items():
            counts = collections.Counter()
            reasons = {}
            alnScores = collections.defaultdict(list)
            insertSizes = collections.defaultdict(list)

            # collect stats
            for alnCollection in sample.alnCollections:
                allele = alnCollection.choice
                counts[allele] += 1

                if not allele in reasons:
                    reasons[allele] = collections.Counter()

                reasons[allele][alnCollection.why] += 1
                alnScores[allele].append(sum(aln.score for aln in alnCollection.chosenSet().getAlignments()))
                insertSizes[allele].append(len(alnCollection.chosenSet()))



            # record stats
            for allele, count in counts.items():
                self.stats.append([variant, sampleName, allele, "count", count])

            for allele in reasons:
                for reason in reasons[allele]:
                    self.stats.append([variant, sampleName, allele, "reason_{}".format(reason), reasons[allele][reason]])

            for allele in alnScores:
                self.stats.append([variant, sampleName, allele, "alnScore_mean", numpy.mean(alnScores[allele])])
                self.stats.append([variant, sampleName, allele, "alnScore_std", numpy.std(alnScores[allele])])

            for allele in insertSizes:
                self.stats.append([variant, sampleName, allele, "insertSize_mean", numpy.mean(insertSizes[allele])])
                self.stats.append([variant, sampleName, allele, "insertSize_std", numpy.std(insertSizes[allele])])



    def __str__(self):
        s = []
        s.append("\t".join(self.header))
        for stat in self.stats:
            s.append("\t".join(str(x) for x in stat))
        return "\n".join(s)

    def saveToPath(self, path):
        f = open(path, "w")
        f.write(str(self))

    def display(self):
        try:
            import pandas
            pandas.options.display.width = 250
            pandas.options.display.max_rows = 400
            df = pandas.DataFrame(self.stats, columns=self.header)
            print(df.pivot_table(values="value", index=["variant","sample","allele"], columns="key"))
        except:
            print(str(self))






"""

variant     sample  allele  key             value
variant1    sample1 alt     count           35
variant1    sample1 alt     alnScore_mean   190
variant1    sample1 alt     reason_orientation     32
variant1    sample1 alt     reason_alnScore     32

"""