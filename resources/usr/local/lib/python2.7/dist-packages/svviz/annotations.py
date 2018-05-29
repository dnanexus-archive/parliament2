import pysam
from svviz.tabix import ensureIndexed


class AnnotationSet(object):
    def __init__(self, tabixPath, preset="bed"):
        self.preset = preset
        self.tabixPath = ensureIndexed(tabixPath, self.preset)
        self._tabix = None
        self.usingChromFormat = False

        self._checkChromFormat()

    def __getstate__(self):
        """ allows pickling of DataHub()s """
        state = self.__dict__.copy()
        state["_tabix"] = None
        return state

    @property
    def tabix(self):
        if self._tabix is None:
            self._tabix = pysam.Tabixfile(self.tabixPath)
        return self._tabix
    
    def _checkChromFormat(self):
        usingChromFormat = 0
        count = 0
        for anno in self.tabix.fetch():
            if anno.startswith("#"):
                continue
            if anno.startswith("chr"):
                self.usingChromFormat += 1
            if count > 10:
                break
            count += 1

        if usingChromFormat / float(count) > 0.8:
            self.usingChromFormat = True

    def fixChromFormat(self, chrom):        
        if not chrom.startswith("chr") and self.usingChromFormat:
            chrom = "chr" + str(chrom)
        if chrom.startswith("chr") and not self.usingChromFormat:
            chrom = chrom.replace("chr", "")
        return chrom


    def getAnnotations(self, chrom, start, end, clip=False):
        """ Returns annotations, in genome order, from the requested genomic region """
        annotations = []

        chrom = self.fixChromFormat(chrom)
        if chrom not in self.tabix.contigs:
            return []
            
        for row in self.tabix.fetch(chrom, start, end):
            values = row.split("\t")
            anno = Annotation(values[0], values[1], values[2], values[5], values[3])
            if clip:
                anno.start = max(anno.start, start)
                anno.end = min(anno.end, end)
            annotations.append(anno)

        return annotations



class Annotation(object):
    def __init__(self, chrom, start, end, strand, name, info=None):
        self.chrom = chrom
        self.start = int(start)
        self.end = int(end)
        self.strand = strand
        self.name = name

        self.info = info if info is not None else {}

    @property
    def label(self):
        return self.name