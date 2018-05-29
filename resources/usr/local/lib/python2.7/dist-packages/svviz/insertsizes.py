import collections
import logging
import os
import tempfile
import numpy

from svviz.utilities import mean, stddev
from svviz.kde import gaussian_kde
from svviz import plotting

def removeOutliers(data, m = 10.):
    """ a method of trimming outliers from a list/array using 
    outlier-safe methods of calculating the center and variance;
    only removes the upper tail, not the lower tail """
    if len(data) < 2:
        return data
        
    data = numpy.array(data)
    d_abs = numpy.abs(data - numpy.median(data))
    d = data - numpy.median(data)
    mdev = numpy.median(d_abs)
    s = d/mdev if mdev else 0.
    return data[s<m]

def chooseOrientation(orientations):
    logging.info("  counts +/-:{:<6} -/+:{:<6} +/+:{:<6} -/-:{:<6} unpaired:{:<6}".format(orientations[False, True], 
                                                    orientations[True, False], 
                                                    orientations[True, True],
                                                    orientations[False, False],
                                                    orientations["unpaired"]))
    ranked = sorted(orientations, key=lambda x: orientations[x])
    chosenOrientations = [ranked.pop()]
    while len(ranked) > 0:
        candidate = ranked.pop()
        if orientations[chosenOrientations[-1]] < 2* orientations[candidate]:
            chosenOrientations.append(candidate)
        else:
            break
    if chosenOrientations[0] == "unpaired":
        chosenOrientations = "any"
    else:
        d = {False: "+", True:"-"}
        chosenOrientations = ["".join(d[x] for x in o) for o in chosenOrientations]
    return chosenOrientations

def getSearchRegions(bam, minLength=0):
    # get the chromosomes and move X, Y, M/MT to the end
    chromosomes = []
    for i in range(bam.nreferences):
        if bam.lengths[i] > minLength:
            chromosomes.append(bam.getrname(i))

    for start, end in [(2500000, 50000000), (None, None)]:
        for chrom in sorted(chromosomes):
            yield chrom, start, end

def sampleInsertSizes(bam, maxreads=50000, skip=0, minmapq=40, maxExpectedSize=20000, keepReads=False):
    """ get the insert size distribution, cutting off the tail at the high end, 
    and removing most oddly mapping pairs

    50,000 reads seems to be sufficient to get a nice distribution, and higher values
        don't tend to change the distribution much """

    inserts = []
    readLengths  = []
    
    count = 0
    reads = []

    orientations = collections.Counter()
    NMs = []
    INDELs = []

    for chrom, start, end in getSearchRegions(bam):
        for read in bam.fetch(chrom, start, end):
            if skip > 0:
                skip -= 1
                continue

            try:
                NMs.append(read.opt("NM")/float(len(read.seq)))
            except KeyError:
                pass

            try:
                INDELs.append(sum(1 for i in zip(*read.cigartuples)[1] if i in[1,2])/float(len(read.seq)))
            except TypeError:
                pass

            if orientations["unpaired"] > 2500 and count < 1000:
                # bail out early if it looks like it's single-ended
                break

            if not read.is_paired:
                orientations["unpaired"] += 1
                readLengths.append(len(read.seq))
                continue
                
            if not read.is_read1:
                continue
            
            if not read.is_proper_pair:
                continue
            if read.is_unmapped or read.mate_is_unmapped:
                continue
            if read.tid != read.rnext:
                continue
            if read.mapq < minmapq:
                continue
            
            # if abs(read.isize) < 20000:
            inserts.append(abs(read.isize))

            curOrient = (read.is_reverse, read.mate_is_reverse)
            if read.reference_start > read.next_reference_start:
                curOrient = not curOrient[0], not curOrient[1]
            orientations[curOrient] += 1
            readLengths.append(len(read.seq))

            if keepReads:
                reads.append(read)

            count += 1
            if count > maxreads:
                break
        if count >= maxreads:
            break

    chosenOrientations = chooseOrientation(orientations)

    return removeOutliers(inserts), reads, chosenOrientations, numpy.array(readLengths)


class ReadStatistics(object):
    def __init__(self, bam, keepReads=False):
        self.insertSizes = []
        self.readLengths = []
        self.orientations = []
        self._insertSizeKDE = None
        self.singleEnded = False

        self._insertSizeScores = {} # cache

        try:
            self.insertSizes, self.reads, self.orientations, self.readLengths = sampleInsertSizes(bam, keepReads=keepReads)
            if len(self.insertSizes) > 1:
                logging.info("  insert size mean: {:.2f} std: {:.2f}".format(numpy.mean(self.insertSizes), numpy.std(self.insertSizes)))
        except ValueError as e:
            print("*"*100, "here")
            print("ERROR:", e)

    def hasInsertSizeDistribution(self):
        if len(self.insertSizes) > 1000:
            return True
        return False

    def meanInsertSize(self):
        if self.hasInsertSizeDistribution():
            return mean(self.insertSizes)
        return None

    def stddevInsertSize(self):
        if self.hasInsertSizeDistribution():
            return stddev(self.insertSizes)
        return None


    def scoreInsertSize(self, isize):
        if not self.hasInsertSizeDistribution():
            return 0

        if self._insertSizeKDE is None:
            self._insertSizeKDE = gaussian_kde(self.insertSizes)

        # the gaussian kde call is pretty slow with ~50,000 data points in it, so we'll cache the result for a bit of a speed-up
        isize = abs(isize)
        if not isize in self._insertSizeScores:
            self._insertSizeScores[isize] = self._insertSizeKDE(isize)

        return self._insertSizeScores[isize]


    def hasReadLengthDistribution(self):
        if len(self.readLengths) > 1000:
            return True
        return False

    def meanReadLength(self):
        if self.hasReadLengthDistribution():
            return mean(self.readLengths)
        return None

    def stddevReadLength(self):
        if self.hasReadLengthDistribution():
            return stddev(self.readLengths)
        return None

    def readLengthUpperQuantile(self):
        if self.hasReadLengthDistribution():
            return numpy.percentile(self.readLengths, 99)
        return None


def plotInsertSizeDistribution(isd, sampleName, dataHub):
    try:
        from rpy2 import robjects as ro

        d = tempfile.mkdtemp()
        filename = os.path.join(d, sampleName)

        if not filename.endswith(".png"):
            filename += ".png"

        ro.r.png(filename, res=250, width=1200, height=1200)

        alleles = ["alt", "ref", "amb"]
        others = [[len(chosenSet) for chosenSet in dataHub.samples[sampleName].chosenSets(allele)] for allele in alleles]
        plotting.ecdf([isd.insertSizes]+others, ["average"]+alleles, xlab="Insert size (bp)", main=sampleName, legendWhere="bottomright", lwd=2)
        
        ro.r["dev.off"]()

        data = open(filename).read()
        return data
    except ImportError:
        return None    
