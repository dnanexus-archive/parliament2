class FlankingRegionCollection(object):
    """
    Used to store information about genomic regions that are 'flanking', meaning they are not really 
    involved in the structural variant; use this to identify reads mapping to the flanking regions
    to provide more context for events and to better categorize ambiguously mapping reads (ie those
    that in the flanks vs those that don't really match either allele)
    """

    def __init__(self, variant):
        self.variant = variant

        commonSegmentIDs = variant.commonSegments()

        # allele -> part -> segment-bounds
        self.alleleFlanks = {}

        for allele in ["ref", "alt"]:
            self.alleleFlanks[allele] = AlleleFlankingRegion(variant, allele, commonSegmentIDs)

    def isFlanking(self, alignmentSet, allele):
        return self.alleleFlanks[allele].isFlanking(alignmentSet)



class AlleleFlankingRegion(object):
    def __init__(self, variant, allele, commonSegmentIDs):
        self.partsToFlankingRegions = {}

        for part in variant.chromParts(allele):
            curpos = 0
            self.partsToFlankingRegions[part.id] = []
            for segment in part.segments:
                end = curpos + len(segment) - 1
                if segment.id in commonSegmentIDs:
                    flankingRegion = {"part":part.id, "segment":segment.id, "start":curpos, "end":end}
                    self.partsToFlankingRegions[part.id].append(flankingRegion)
                curpos = end + 1


    def isFlanking(self, alignmentSet):
        alignments = alignmentSet.getAlignments()
        segments = set()
        partIDs = set()

        for alignment in alignments:
            partID = alignment.regionID
            partIDs.add(partID)
            if len(partIDs) > 1:
                return False

            for flankingRegion in self.partsToFlankingRegions[partID]:
                if flankingRegion["start"] < alignment.start and alignment.end < flankingRegion["end"]:
                    segments.add(flankingRegion["segment"])
                    if len(segments) > 1: return False

        if len(segments) == 1:
            return True
        return False




