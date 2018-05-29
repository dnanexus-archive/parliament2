import collections
import logging

from svviz.utilities import Locus, getListDefault
from svviz import genomesource


def nonNegative(x):
    return max(x, 0)
    

class ChromPart(object):
    def __init__(self, regionID, segments, sources):
        self.id = regionID
        self.segments = segments
        self.sources = sources
        self._seq = None

    def getSeq(self, start=0, end=None):
        if self._seq is None:
            seqs = []
            for segment in self.segments:
                seq = self.sources[segment.source].getSeq(segment.chrom, segment.start, segment.end, segment.strand)
                seqs.append(seq)
            self._seq = "".join(seqs).upper()
        if end is None:
            end = len(self._seq)
        return self._seq[start:end]

    def __len__(self):
        return len(self.getSeq())

    def __repr__(self):
        return "{}:{}".format(self.id, self.segments)

class ChromPartsCollection(object):
    def __init__(self, parts=None):
        self.parts = collections.OrderedDict()
        if parts is not None:
            for part in parts:
                self.parts[part.id] = part

    def getPart(self, id_):
        return self.parts[id_]

    def getSeq(self, id_, *args, **kwdargs):
        return self.parts[id_].getSeq(*args, **kwdargs)

    def __iter__(self):
        return iter(self.parts.values())
    def __len__(self):
        return len(self.parts)

def getBreakpointFormatsStr(which=None):
    formats = []
    if which in ["del", None]:
        formats.append("Format for deletion (-t del) breakpoints is '<chrom> <start> <end>'")
    if which in ["ldel", None]:
        formats.append("Format for largedeletion (-t ldel) breakpoints is '<chrom> <start> <end>'")
    if which in ["ins", None]:
        formats.append("Format for insertion (-t ins) breakpoints is '<chrom> <pos> [end] <seq>'; \n"
            "  specify 'end' to create a compound deletion-insertion, otherwise insertion \n"
            "  position is before 'pos'")
    if which in ["inv", None]:
        formats.append("Format for inversion (-t inv) breakpoints is '<chrom> <start> <end>'")
    if which in ["mei", None]:
        formats.append( "Format for mobile element insertion (-t mei) is '<mobile_elements.fasta> \n"
            "  <chrom> <pos> <ME name> [ME strand [start [end]]]'")
    if which in ["tra", None]:
        formats.append( "Format for a translocation (-t tra) is 'chrom1 start1 chrom2 start2 orientation'")
    if which in ["bkend", None]:
        formats.append( "Format for a breakend (-t bkend) is 'chrom1 start1 strand1 chrom2 start2 strand2'")
    return "\n".join(formats)


def getVariant(dataHub):
    if dataHub.args.type.lower().startswith("del"):
        assert len(dataHub.args.breakpoints) == 3, getBreakpointFormatsStr("del")
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        assert start < end
        variant = Deletion.from_breakpoints(chrom, start-1, end-1, dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower() in ["ldel", "largedeletion"]:
        assert len(dataHub.args.breakpoints) == 3, getBreakpointFormatsStr("ldel")
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        assert start < end
        variant = LargeDeletion.from_breakpoints(chrom, start-1, end-1, dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower().startswith("ins"):
        assert len(dataHub.args.breakpoints) in [3,4], getBreakpointFormatsStr("ins")
        chrom = dataHub.args.breakpoints[0]
        pos = int(dataHub.args.breakpoints[1])
        if len(dataHub.args.breakpoints) == 3:
            seq = dataHub.args.breakpoints[2]
            end = pos
        else:
            end = int(dataHub.args.breakpoints[2])
            seq = dataHub.args.breakpoints[3]
        variant = Insertion(Locus(chrom, pos, end, "+"), seq, dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower().startswith("inv"):
        assert len(dataHub.args.breakpoints) == 3, getBreakpointFormatsStr("inv")
        chrom = dataHub.args.breakpoints[0]
        start = int(dataHub.args.breakpoints[1])
        end = int(dataHub.args.breakpoints[2])
        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1
        variant = Inversion(Locus(chrom, start, end, "+"), dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower().startswith("mei"):
        assert len(dataHub.args.breakpoints) >= 4, getBreakpointFormatsStr("mei")

        insertionBreakpoint = Locus(dataHub.args.breakpoints[1], dataHub.args.breakpoints[2], dataHub.args.breakpoints[2], "+")

        meName = dataHub.args.breakpoints[3]
        meStrand = getListDefault(dataHub.args.breakpoints, 4, "+")
        meStart = getListDefault(dataHub.args.breakpoints, 5, 0)
        meEnd = getListDefault(dataHub.args.breakpoints, 6, 1e100)

        meCoords = Locus(meName, meStart, meEnd, meStrand)
        meFasta = genomesource.FastaGenomeSource(dataHub.args.breakpoints[0])

        variant = MobileElementInsertion(insertionBreakpoint, meCoords, meFasta, dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower().startswith("tra"):
        assert len(dataHub.args.breakpoints) == 5, getBreakpointFormatsStr("tra")
        chrom1 = dataHub.args.breakpoints[0]
        start1 = int(dataHub.args.breakpoints[1])

        chrom2 = dataHub.args.breakpoints[2]
        start2 = int(dataHub.args.breakpoints[3])

        orientation = dataHub.args.breakpoints[4]

        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        variant = Translocation(Locus(chrom1, start1, start1, "+"), 
                                Locus(chrom2, start2, start2, orientation), 
                                dataHub.alignDistance, dataHub.genome)

    elif dataHub.args.type.lower() in ["bkend", "breakend"]:
        assert len(dataHub.args.breakpoints) == 6, getBreakpointFormatsStr("bkend")
        chrom1 = dataHub.args.breakpoints[0]
        start1 = int(dataHub.args.breakpoints[1])
        strand1 = dataHub.args.breakpoints[2]

        chrom2 = dataHub.args.breakpoints[3]
        start2 = int(dataHub.args.breakpoints[4])
        strand2 = dataHub.args.breakpoints[5]

        if dataHub.args.min_mapq is None:
            dataHub.args.min_mapq = -1

        variant = Breakend(Locus(chrom1, start1, start1, strand1), 
                           Locus(chrom2, start2, start2, strand2), 
                           dataHub.alignDistance, dataHub.genome)
    else:
        raise Exception("only accept event types of deletion, insertion, mei, translocation or breakend")
    logging.info(" Variant: {}".format(variant))

    return variant



class Segment(object):
    colors = {0:"red", 1:"blue", 2:"gray", 3:"orange", 4:"brown"}

    def __init__(self, chrom, start, end, strand, id_, source="genome"):
        self.chrom = chrom
        if start > end:
            start, end = end, start

        if start < 0:
            start = 0
        if end < 0:
            raise Exception("Segment end coordinate cannot be negative: {}".format(start))
        self.start = start
        self.end = end
        self.strand = strand
        self.id = id_
        self.source = source

    def __len__(self):
        return abs(self.end - self.start)

    def color(self):
        return self.colors[self.id]

    def antisense(self):
        antisense = {"+":"-", "-":"+"}
        return Segment(self.chrom, self.start, self.end, antisense[self.strand], self.id, self.source)

    def __repr__(self):
        return "<Segment {} {}:{}-{}{} (len={};{})>".format(self.id, self.chrom, self.start, self.end, self.strand, 
            len(self), self.source)

def mergedSegments(segments):
    # quick-and-dirty recursive function to merge adjacent variant.Segment's
    if len(segments) == 1:
        return segments

    done = []
    for i in range(len(segments)-1):
        first = segments[i]
        second = segments[i+1]

        if first.strand == "+" and first.chrom==second.chrom and first.strand==second.strand and first.end == second.start-1 and first.source==second.source:
                merged = Segment(first.chrom, first.start, second.end, second.strand, "{}_{}".format(first.id, second.id), first.source)
                result = done + mergedSegments([merged]+segments[i+2:])
                return result
        elif first.strand == "-" and first.chrom==second.chrom and first.strand==second.strand and first.start == second.end+1 and first.source==second.source:
                merged = Segment(first.chrom, first.end, second.start, second.strand, "{}_{}".format(first.id, second.id), first.source)
                result = done + mergedSegments([merged]+segments[i+2:])
                return result

        else:
            done.append(segments[i])

    done.append(segments[-1])
    return done
    
class StructuralVariant(object):
    def __init__(self, breakpoints, alignDistance, genomeSource):
        self.breakpoints = sorted(breakpoints, key=lambda x: (x.chr(), x.start()))
        self.alignDistance = alignDistance

        self.sources = {"genome":genomeSource}

        self._seqs = {}

    def __getstate__(self):
        """ allows pickling of StructuralVariant()s """
        for allele in ["alt", "ref"]:
            for part in self.chromParts(allele):
                part.getSeq()
        state = self.__dict__.copy()
        return state


    def __str__(self):
        return "{}({};{})".format(self.__class__.__name__, self.breakpoints, self.alignDistance)
    def shortName(self):
        return "{}_{}_{}".format(self.__class__.__name__[:3].lower(), self.breakpoints[0].chr(), self.breakpoints[0].start())

    def searchRegions(self):
        pass    

    def chromParts(self, allele):
        """ overload this method for multi-part variants """
        segments = self.segments(allele)
        
        name = "{}_part".format(allele)
        if allele == "amb":
            name = "ref_part"

        parts = [ChromPart(name, segments, self.sources)]
        return ChromPartsCollection(parts)   

    def segments(self, allele):
        raise Exception("use .parts() instead!")
        # for visual display of the different segments between breakpoints
        return None

    def _segments(self, allele):
        segments = []
        for part in self.chromParts(allele):
            segments.extend(part.segments)
        return segments

    def commonSegments(self):
        """ return the segment IDs of the segments that are identical between 
        the ref and alt alleles (eg, flanking regions) """
        common = []
        refCounter = collections.Counter((segment.id for segment in self._segments("ref")))
        altCounter = collections.Counter((segment.id for segment in self._segments("alt")))
        if max(refCounter.values()) > 1 or max(altCounter.values()) > 1:
            logging.warn(" Same genomic region repeated multiple times within one allele; "
                "all flanking reads will be marked as ambiguous")
            return []


        refSegments = dict((segment.id, segment) for segment in self._segments("ref"))
        altSegments = dict((segment.id, segment) for segment in self._segments("alt"))

        for segmentID, refSegment in refSegments.items():
            if not segmentID in altSegments:
                continue
            altSegment = altSegments[segmentID]

            # Could remove the requirement to have the strand be the same
            # allowing the reads within the inversion to be plotted too
            if refSegment.chrom==altSegment.chrom and \
                refSegment.start == altSegment.start and \
                refSegment.end == altSegment.end and \
                refSegment.strand == altSegment.strand and \
                refSegment.source == altSegment.source:
                common.append(segmentID)

        return common


class Deletion(StructuralVariant):
    @classmethod
    def from_breakpoints(class_, chrom, first, second, alignDistance, fasta):
        breakpointLoci = [Locus(chrom, first, first, "+"), Locus(chrom, second, second, "+")]
        return class_(breakpointLoci, alignDistance, fasta)

    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        deletionRegion = Locus(chrom, nonNegative(self.breakpoints[0].start()-searchDistance), 
            self.breakpoints[-1].end()+searchDistance, "+")
        return [deletionRegion]

    def deletionLength(self):
        length = self.breakpoints[1].end() - self.breakpoints[0].start()
        return length

    def segments(self, allele):
        chrom = self.breakpoints[0].chr()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[0].start(), self.breakpoints[1].end(), "+", 1),
                    Segment(chrom, self.breakpoints[1].end()+1, self.breakpoints[1].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[1].end()+1, self.breakpoints[1].end()+self.alignDistance, "+", 2)]

    def __str__(self):
        return "{}::{}:{:,}-{:,}({})".format(self.__class__.__name__, self.breakpoints[0].chr(), self.breakpoints[0].start(), 
            self.breakpoints[1].end(), self.deletionLength())


class Inversion(StructuralVariant):
    def __init__(self, region, alignDistance, fasta):
        breakpoints = [Locus(region.chr(), region.start(), region.start(), "+"), Locus(region.chr(), region.end(), region.end(), "+")]
        super(Inversion, self).__init__(breakpoints, alignDistance, fasta)

        self.region = region

    def chrom(self):
        return self.region.chr()

    def searchRegions(self, searchDistance):
        chrom = self.chrom()

        if len(self.region) < 2*searchDistance:
            # return a single region
            return [Locus(chrom, nonNegative(self.region.start()-searchDistance), self.region.end()+searchDistance, "+")]
        else:
            # return two regions, each around one of the ends of the inversion
            searchRegions = []
            searchRegions.append(Locus(chrom, nonNegative(self.region.start()-searchDistance), 
                self.region.start()+searchDistance, "+"))
            searchRegions.append(Locus(chrom, nonNegative(self.region.end()-searchDistance), 
                self.region.end()+searchDistance, "+"))
            return searchRegions

    def segments(self, allele):
        chrom = self.chrom()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.region.start()-self.alignDistance, self.region.start()-1, "+", 0),
                    Segment(chrom, self.region.start(), self.region.end(), "+", 1),
                    Segment(chrom, self.region.end()+1, self.region.end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.region.start()-self.alignDistance, self.region.start()-1, "+", 0),
                    Segment(chrom, self.region.start(), self.region.end(), "-", 1),
                    Segment(chrom, self.region.end()+1, self.region.end()+self.alignDistance, "+", 2)]

                
    def __str__(self):
        return "{}::{}:{:,}-{:,}".format(self.__class__.__name__, self.region.chr(), self.region.start(), self.region.end())


class Insertion(StructuralVariant):
    def __init__(self, breakpoint, insertSeq, alignDistance, fasta):
        super(Insertion, self).__init__([breakpoint], alignDistance, fasta)
        self.sources["insertion"] = genomesource.GenomeSource(insertSeq)
        self.insertionLength = len(insertSeq)

    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        return [Locus(chrom, nonNegative(self.breakpoints[0].start()-searchDistance), 
            self.breakpoints[-1].end()+searchDistance, "+")]

    def segments(self, allele):
        breakpoint = self.breakpoints[0]
        chrom = breakpoint.chr()

        # If breakpoint has no length, we make the insertion before the breakpoint coordinate
        deletionOffset = 0
        if len(breakpoint) > 1:
            # If we're deleting some bases in addition to inserting, we'll make sure to start
            # the last segment after the deleted bases
            deletionOffset = 1

        if allele in ["ref", "amb"]:
            refSegments = []
            refSegments.append(Segment(chrom, breakpoint.start()-self.alignDistance, breakpoint.start()-1, "+", 0))
            if len(breakpoint) > 1:
                refSegments.append(Segment(chrom, breakpoint.start(), breakpoint.end(), "+", 3))

            refSegments.append(Segment(chrom, breakpoint.end()+deletionOffset, breakpoint.end()+self.alignDistance, "+", 2))
            return refSegments
        elif allele == "alt":
            return [Segment(chrom, breakpoint.start()-self.alignDistance, breakpoint.start()-1, "+", 0),
                    Segment("insertion", 0, self.insertionLength, "+", 1, source="insertion"),
                    Segment(chrom, breakpoint.end()+deletionOffset, breakpoint.end()+self.alignDistance, "+", 2)]

    def __str__(self):
        if len(self.breakpoints[0]) > 1:
            return "{}::{}:{:,}-{:,};len={}".format(self.__class__.__name__, 
                                                  self.breakpoints[0].chr(), 
                                                  self.breakpoints[0].start(), 
                                                  self.breakpoints[0].end(),
                                                  self.insertionLength)

        return "{}::{}:{:,};len={}".format(self.__class__.__name__, self.breakpoints[0].chr(), self.breakpoints[0].start(), self.insertionLength)
       

class MobileElementInsertion(StructuralVariant):
    def __init__(self, breakpoint, insertedSeqLocus, insertionFasta, alignDistance, refFasta):
        super(MobileElementInsertion, self).__init__([breakpoint], alignDistance, refFasta)

        self.sources["repeats"] = insertionFasta
        self.insertedSeqLocus = insertedSeqLocus


    def searchRegions(self, searchDistance):
        chrom = self.breakpoints[0].chr()
        return [Locus(chrom, nonNegative(self.breakpoints[0].start()-searchDistance), 
            self.breakpoints[-1].end()+searchDistance, "+")]

    def segments(self, allele):
        chrom = self.breakpoints[0].chr()

        if allele in ["ref", "amb"]:
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(chrom, self.breakpoints[0].end(), self.breakpoints[0].end()+self.alignDistance, "+", 2)]
        elif allele == "alt":
            return [Segment(chrom, self.breakpoints[0].start()-self.alignDistance, self.breakpoints[0].start()-1, "+", 0),
                    Segment(self.insertedSeqLocus.chr(), self.insertedSeqLocus.start(), 
                        self.insertedSeqLocus.end(), self.insertedSeqLocus.strand(), 1, source="repeats"),
                    Segment(chrom, self.breakpoints[0].end(), self.breakpoints[0].end()+self.alignDistance, "+", 2)]

    def __str__(self):
        return "{}::{}({});{})".format(self.__class__.__name__, self.insertedSeqLocus.chr(), self.breakpoints, len(self.insertedSeqLocus))
    def shortName(self):
        return "{}_{}_{}".format("mei", self.breakpoints[0].chr(), self.breakpoints[0].start())


class Translocation(StructuralVariant):
    def __init__(self, breakpoint1, breakpoint2, alignDistance, refFasta):
        super(Translocation, self).__init__([breakpoint1, breakpoint2], alignDistance, refFasta)

        self.breakpoints = [breakpoint1, breakpoint2]

    def searchRegions(self, searchDistance):
        searchRegions = []

        for breakpoint in self.breakpoints:
            searchRegions.append(Locus(breakpoint.chr(), nonNegative(breakpoint.start()-searchDistance), 
                breakpoint.end()+searchDistance, breakpoint.strand()))

        return searchRegions

    def chromParts(self, allele):
        parts = []
        b1 = self.breakpoints[0]
        b2 = self.breakpoints[1]

        segments = []
        for i, breakpoint in enumerate(self.breakpoints):
            segments.append(Segment(breakpoint.chr(), breakpoint.start()-self.alignDistance, 
                                    breakpoint.start()-1, breakpoint.strand(), 0+i*2))
            segments.append(Segment(breakpoint.chr(), breakpoint.start(), 
                                    breakpoint.start()+self.alignDistance, breakpoint.strand(), 1+i*2))
            # assert breakpoint.strand() == "+", breakpoint

        if b2.strand() == "-":
            if allele in ["ref", "amb"]:
                name = "ref_{}".format(b1.chr())
                parts.append(ChromPart(name, [segments[0], segments[1]], self.sources))

                name = "ref_{}".format(b2.chr())
                if b1.chr() == b2.chr(): name += "b"
                parts.append(ChromPart(name, [segments[3], segments[2]], self.sources))


            elif allele == "alt":
                name = "alt_{}/{}".format(b1.chr(), b2.chr())
                parts.append(ChromPart(name, [segments[0], segments[2]], self.sources))

                name = "alt_{}/{}".format(b2.chr(), b1.chr())
                if b1.chr() == b2.chr(): name += "b"

                parts.append(ChromPart(name, [segments[3], segments[1]], self.sources))
        else:
            if allele in ["ref", "amb"]:
                name = "ref_{}".format(b1.chr())
                part = ChromPart(name, segments[:2], self.sources)
                parts.append(part)

                name = "ref_{}".format(b2.chr())
                if b1.chr() == b2.chr(): name += "b"

                part = ChromPart(name, segments[2:], self.sources)
                parts.append(part)

            elif allele == "alt":
                name = "alt_{}/{}".format(b1.chr(), b2.chr())
                parts.append(ChromPart(name, [segments[0], segments[3]], self.sources))

                name = "alt_{}/{}".format(b2.chr(), b1.chr())
                if b1.chr() == b2.chr(): name += "b"

                parts.append(ChromPart(name, [segments[2], segments[1]], self.sources))


        return ChromPartsCollection(parts) 

    def __str__(self):
        chrom1 = self.breakpoints[0].chr()
        chrom2 = self.breakpoints[1].chr()
        if not chrom1.startswith("chr"):
            chrom1 = "chr{}".format(chrom1)
            chrom2 = "chr{}".format(chrom2)
        return "{}::{}:{:,}/{}:{:,}".format(self.__class__.__name__, chrom1, self.breakpoints[0].start(), chrom2, self.breakpoints[1].start())

class Breakend(StructuralVariant):
    def __init__(self, breakpoint1, breakpoint2, alignDistance, refFasta):
        super(Breakend, self).__init__([breakpoint1, breakpoint2], alignDistance, refFasta)

        self.breakpoints = [breakpoint1, breakpoint2]
        self.chromParts("alt")

    def searchRegions(self, searchDistance):
        searchRegions = []

        for breakpoint in self.breakpoints:
            searchRegions.append(Locus(breakpoint.chr(), nonNegative(breakpoint.start()-searchDistance), 
                breakpoint.end()+searchDistance, breakpoint.strand()))

        return searchRegions

    def chromParts(self, allele):
        b1 = self.breakpoints[0]
        b2 = self.breakpoints[1]

        segments = []
        for i, breakpoint in enumerate(self.breakpoints):
            segments.append(Segment(breakpoint.chr(), breakpoint.start()-self.alignDistance, 
                                    breakpoint.start()-1, "+", 0+i*2))
            segments.append(Segment(breakpoint.chr(), breakpoint.start(), 
                                    breakpoint.start()+self.alignDistance, "+", 1+i*2))
            # assert breakpoint.strand() == "+", breakpoint

        # TODO: disambiguate reads mapping to multiple parts with the same alignment scores
        # but different orientations
        loci = [Locus(s.chrom, s.start, s.end, "+") for s in segments]
        for i in range(len(loci)-1):
            for j in range(i+1, len(loci)):
                if loci[i].overlaps(loci[j]):
                    raise Exception("Not yet implemented - breakend-breakpoints near one another")

        parts = []
        if allele in ["ref", "amb"]:
            name = "ref_{}".format(b1.chr())
            parts.append(ChromPart(name, [segments[0], segments[1]], self.sources))

            name = "ref_{}".format(b2.chr())
            if b1.chr() == b2.chr(): name += "b"
            parts.append(ChromPart(name, [segments[2], segments[3]], self.sources))

        else:
            if b1.strand() == "+": s1 = segments[0]
            else: s1 = segments[1].antisense()

            if b2.strand() == "+": s2 = segments[3]
            else: s2 = segments[2].antisense()
            
            name = "alt_{}/{}".format(b1.chr(), b2.chr())
            parts.append(ChromPart(name, [s1, s2], self.sources))


        return ChromPartsCollection(parts) 

    def __str__(self):
        chrom1 = self.breakpoints[0].chr()
        chrom2 = self.breakpoints[1].chr()
        if not chrom1.startswith("chr"):
            chrom1 = "chr{}".format(chrom1)
            chrom2 = "chr{}".format(chrom2)
        return "{}::{}:{:,}/{}:{:,}".format(self.__class__.__name__, chrom1, self.breakpoints[0].start(), chrom2, self.breakpoints[1].start())



class LargeDeletion(Breakend):
    @classmethod
    def from_breakpoints(class_, chrom, first, second, alignDistance, fasta):
        breakpoint1 = Locus(chrom, first, first, "+")
        breakpoint2 = Locus(chrom, second, second, "+")
        return class_(breakpoint1, breakpoint2, alignDistance, fasta)

    def deletionLength(self):
        return self.breakpoints[1].end() - self.breakpoints[0].start()

    def __str__(self):
        return "{}::{}:{:,}-{:,}({})".format(self.__class__.__name__, self.breakpoints[0].chr(), self.breakpoints[0].start(), 
            self.breakpoints[1].end(), self.deletionLength())