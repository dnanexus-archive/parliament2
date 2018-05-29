""" Simple parser for gff/gtf format genes, indexed by tabix """

import collections
import re
from svviz.annotations import AnnotationSet, Annotation

RE_TRANSCRIPT = r".*transcript_id \"([^\"]*)\".*"
RE_GENE_ID = r".*gene_id \"([^\"]*)\".*"
RE_GENE_NAME = r".*gene_name \"([^\"]*)\".*"
RE_LINE = r"(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)\t(.*)"



class GeneAnnotationSet(AnnotationSet):
    def __init__(self, tabixPath):
        super(GeneAnnotationSet, self).__init__(tabixPath, preset="gff")
    
    def getAnnotations(self, chrom, start, end, clip=False, extension=1000000):
        chrom = self.fixChromFormat(chrom)
        
        lines = self.tabix.fetch(chrom, max(0, start-extension), end+extension)

        transcriptsToLines = collections.defaultdict(list)

        for i, line in enumerate(lines):
            if len(line) < 2:
                continue    

            try:            
                tx = re.match(RE_TRANSCRIPT, line).group(1)
            except AttributeError:
                tx = "anno{}".format(i)


            transcriptsToLines[tx].append(line)

        genes = []
        for transcript, lines in transcriptsToLines.items():
            genes.append(GTFGene(lines))

        if extension > 0:
            genes = [gene for gene in genes if not (end<gene.start or start>gene.end)]#start<=gene.start<=end or start<=gene.end<=end)]

        if clip:
            for gene in genes:
                gene.clip(start, end)

        return genes


class GTFGene(Annotation):
    def __init__(self, gtfLines):
        self.id = None
        self.name = None
        self.chrom = None
        self.start = None
        self.end = None
        self.strand = None
        self.info = None

        self.txExons = []
        self.cdExons = []

        self.fromGTFLines(gtfLines)

    def clip(self, start, end):
        self.start = max(start, self.start)
        self.end = min(end, self.end)

        newTxExons = []
        for txExon in self.txExons:
            curStart, curEnd = txExon
            if curStart>end or curEnd<start:
                continue
            newTxExons.append((max(start, curStart), min(end, curEnd)))
        self.txExons = newTxExons

        newCdExons = []
        for cdExon in self.cdExons:
            curStart, curEnd = cdExon
            if curStart>end or curEnd<start:
                continue
            newCdExons.append((max(start, curStart), min(end, curEnd)))
        self.cdExons = newCdExons

    @property
    def label(self):
        if self.name is not None:
            return self.name
        return self.id

    def fromGTFLines(self, gtfLines):
        for line in gtfLines:
            fields = re.match(RE_LINE, line).groups()

            chrom = fields[0]
            start = int(fields[3])
            end = int(fields[4])
            strand = fields[6]

            event = fields[2]

            gene_id = re.match(RE_TRANSCRIPT, line)
            if gene_id is not None:
                gene_id = gene_id.group(1)
            else:
                gene_id = ""
                
            gene_name = re.match(RE_GENE_NAME, line)
            if gene_name is not None:
                gene_name = gene_name.group(1)

            if self.id is not None and self.id != gene_id:
                raise Exception("transcripts don't belong to the same gene")
            self.id = gene_id
            self.name = gene_name

            if self.strand is not None and self.strand != strand:
                raise Exception("exons aren't on the same strand")
            self.strand = strand

            if self.chrom is not None and self.chrom != chrom:
                raise Exception("exons aren't on the same chromosome")
            self.chrom = chrom

            if self.start is None or start < self.start:
                self.start = start

            if self.end is None or end > self.end:
                self.end = end

            if self.end < self.start:
                self.start, self.end = self.end, self.start

            if event == "CDS":
                self.cdExons.append((start, end))

            if event == "exon":
                self.txExons.append((start, end))


    def __str__(self):
        if self.name is None:
            return "{} {}:{}-{}{} {} {}".format(self.id, self.chrom, self.start, self.end, self.strand, self.txExons, self.cdExons)
        return "{} {}:{}-{}{} {} {}".format(self.name, self.chrom, self.start, self.end, self.strand, self.txExons, self.cdExons)

    def __repr__(self):
        return str(self)

if __name__ == '__main__':
    """ UCSC Genes table exported as gtf, then sorted using:
    gsort -k1,1V -k4,4n -k5,5n /Users/nspies/Downloads/hg19.genes.gtf | bgzip > /Users/nspies/Downloads/hg19.genes.gtf.gz

    (or remove the V option to get it to work with normal OS X sort) """

    gtf = GeneAnnotationSet("/Users/nspies/Downloads/hg19.genes.gtf.gz")
    genes = gtf.getAnnotations("chr12", 66218240, 66360071)

    for gene in genes:
        print(gene)