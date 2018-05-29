import collections
import itertools
import math
import re
from svviz.svg import SVG
from svviz import utilities
from svviz import variants
from svviz import gff

class Scale(object):
    def __init__(self, chromPartsCollection, pixelWidth, dividerSize=25):
        # length is in genomic coordinates, starts is in pixels
        self.dividerSize = dividerSize
        self.partsToLengths = collections.OrderedDict()
        self.partsToStartPixels = collections.OrderedDict()
        self.chromPartsCollection = chromPartsCollection

        for part in chromPartsCollection:
            self.partsToLengths[part.id] = len(part)

        self.pixelWidth = pixelWidth

        totalLength = sum(self.partsToLengths.values()) + (len(self.partsToLengths)-1)*dividerSize
        self.basesPerPixel = totalLength / float(pixelWidth)

        curStart = 0
        for regionID in self.partsToLengths:
            self.partsToStartPixels[regionID] = curStart
            curStart += (self.partsToLengths[regionID]+dividerSize) / self.basesPerPixel

    def topixels(self, g, regionID=None):
        pts = 0
        if regionID != None:
            pts = self.partsToStartPixels[regionID]
        else:
            assert len(self.partsToStartPixels) == 1


        pos = g / float(self.basesPerPixel) + pts
        return pos

    def relpixels(self, g):
        dist = g / float(self.basesPerPixel)
        return dist

    def getBreakpointPositions(self, regionID):
        breakpoints = []

        part = self.chromPartsCollection.parts[regionID]

        curpos = 0
        for segment in part.segments[:-1]:
            curpos += len(segment)
            breakpoints.append(curpos)

        return breakpoints


class Axis(object):
    def __init__(self, scale, variant, allele):
        self.scale = scale
        self.allele = allele
        self.variant = variant
        self.chromPartsCollection = variant.chromParts(allele)
        self.height = 75


    def baseHeight(self):
        return 75

    def render(self, scaleFactor=1.0, spacing=1.0, height=None, thickerLines=False):
        self.height = height
        if height == None:
            self.height = 75 * scaleFactor

        self.svg = SVG(self.scale.pixelWidth, self.height, yrelto="top", headerExtras="""preserveAspectRatio="none" """)

        # dividers! (multi-part only)
        if len(self.chromPartsCollection) > 1:
            for part in list(self.chromPartsCollection)[1:]:
                divWidth = self.scale.relpixels(self.scale.dividerSize)
                x = self.scale.partsToStartPixels[part.id] - divWidth
                self.svg.rect(x, 0, divWidth, self.height, fill="#B2B2B2")
                self.svg.line(x, 0, x, self.height, stroke="black", **{"stroke-width":1*scaleFactor})
                self.svg.line(x+divWidth, 0, x+divWidth, self.height, stroke="black", **{"stroke-width":1*scaleFactor})

            for i, part in enumerate(self.chromPartsCollection):
                if i == 0:
                    x = self.scale.topixels(self.scale.partsToLengths[part.id], part.id) - 15
                    anchor = "end"
                else:
                    x = self.scale.partsToStartPixels[part.id] + 15
                    anchor = "start"
                self.svg.text(x, 18*scaleFactor, part.id, anchor=anchor, size=18*scaleFactor)



        # tick marks and coordinates
        for regionID in self.scale.partsToStartPixels:
            for tick in self.getTicks(regionID):
                x = self.scale.topixels(tick, regionID)

                self.svg.rect(x, 35*scaleFactor, 1*scaleFactor, 15*scaleFactor, fill="black")
                label = tick
                if tick > 1e6:
                    label = "{:.1f}MB".format(tick/1e6)
                elif tick > 1e3:
                    label = "{:.1f}KB".format(tick/1e3)

                if x < 50:
                    x = 50
                elif x > self.scale.pixelWidth - 50:
                    x = self.scale.pixelWidth - 50
                extras = {}
                if thickerLines:
                    extras["font-weight"] = "bold"
                self.svg.text(x, self.height-4*scaleFactor, label, size=18*scaleFactor, **extras)


        # segment arrows
        for part in self.chromPartsCollection:
            curOffset = self.scale.partsToStartPixels[part.id]
            for segment in part.segments:
                start = curOffset
                end = self.scale.relpixels(len(segment)) + curOffset
                curOffset = end

                arrowDirection = "right"

                if segment.strand == "-":
                    start, end = end, start
                    arrowDirection = "left"

                y = 35*scaleFactor

                self.svg.line(start, y, end, y, stroke=segment.color(), **{"stroke-width":8*scaleFactor})
                self.svg.lineWithInternalArrows(start, y, end, y, stroke=segment.color(), direction=arrowDirection,
                    arrowKwdArgs={"class":"scaleArrow"}, **{"stroke-width":3*scaleFactor})

        # breakpoints
        previousPosition = None
        for part in self.chromPartsCollection:
            for vline in self.scale.getBreakpointPositions(part.id):
                thickness = 1*scaleFactor
                if thickerLines:
                    thickness *= 2
                x = self.scale.topixels(vline, part.id)
                self.svg.line(x, 20*scaleFactor, x, 55*scaleFactor, 
                    stroke="black", **{"stroke-width":thickness})
                
                if previousPosition is None or x-previousPosition > 250*scaleFactor:     
                    self.svg.text(x-(scaleFactor/2.0), 18*scaleFactor, "breakpoint", size=18*scaleFactor, fill="black")
                previousPosition = x


        return str(self.svg)

    def getTicks(self, regionID):
        ticks = []
        start = 0
        width = self.scale.partsToLengths[regionID]
        end = start + width

        res = (10 ** round(math.log10(end - start))) / 10.0
        if width / res > 15:
            res *= 2.5
        elif width / res < 5:
            res /= 2.0

        roundStart = start - (start%res)

        for i in range(int(roundStart), end, int(res)):
            ticks.append(i)

        return ticks

NYIWarned = False
class ReadRenderer(object):
    def __init__(self, rowHeight, scale, chromPartsCollection, thickerLines=False, colorCigar=True):
        self.rowHeight = rowHeight
        self.svg = None
        self.scale = scale
        self.chromPartsCollection = chromPartsCollection
        self.thickerLines = thickerLines
        self.colorCigar = colorCigar

        self.nucColors = {"A":"blue", "C":"orange", "G":"green", "T":"black", "N":"gray"}
        self.colorsByStrand = {"+":"purple", "-":"red"}
        self.insertionColor = "cyan"
        self.deletionColor = "gray"
        self.overlapColor = "lime"

    def render(self, alignmentSet):
        yoffset = alignmentSet.yoffset
        if len(set([x.regionID for x in alignmentSet.getAlignments()]))!=1:
            global NYIWarned
            
            if not NYIWarned:            
                NYIWarned = True
                print("\n"*5)
                print("WARNING! Not yet implemented: ambiguous track display of read pairs mapping to different chromosomes")
                print("\n"*5)
            return

        regionID = alignmentSet.getAlignments()[0].regionID
        pstart = self.scale.topixels(alignmentSet.start, regionID)
        pend = self.scale.topixels(alignmentSet.end, regionID)

        isFlanking = (alignmentSet.parentCollection.why == "flanking")

        thinLineWidth = 5
        curColor = "#CCCCCC"
        extras = {}
        if isFlanking:
            extras["class"] = "flanking"
            curColor = "#EEEEEE"

        self.svg.rect(pstart, yoffset-(self.rowHeight/2.0)+thinLineWidth/2.0, pend-pstart, thinLineWidth, fill=curColor, **extras)

        positionCounts = collections.Counter()

        if self.thickerLines:
            # extra "bold":
            ystart = yoffset+3
            height = self.rowHeight+6
        else:
            ystart = yoffset
            height = self.rowHeight


        for alignment in alignmentSet.getAlignments():
            for position in range(alignment.start, alignment.end+1):
                positionCounts[position] += 1

            pstart = self.scale.topixels(alignment.start, regionID)
            pend = self.scale.topixels(alignment.end, regionID)

            curColor = self.colorsByStrand[alignment.strand]
            extras = {"class":"read", "data-cigar":alignment.cigar,"data-readid":alignment.name}
            if isFlanking:
                extras["class"] = "read flanking"
                curColor = "#AAAAAA"

            self.svg.rect(pstart, ystart, pend-pstart, height, fill=curColor, 
                          **extras)

            if self.colorCigar:
                self._drawCigar(alignment, ystart, height, isFlanking)

        highlightOverlaps = True
        if highlightOverlaps and not isFlanking:
            self._highlightOverlaps(positionCounts, ystart, height, regionID, alignment.name, isFlanking)


    def _drawCigar(self, alignment, yoffset, height, isFlanking):
        eachNuc = False # this gets to be computationally infeasible to display in the browser
        pattern = re.compile('([0-9]*)([MIDNSHP=X])')

        genomePosition = alignment.start
        sequencePosition = 0

        chromPartSeq = self.chromPartsCollection.getSeq(alignment.regionID)

        extras = {}
        if isFlanking:
            extras = {"class":"flanking"}
        for length, code in pattern.findall(alignment.cigar):
            length = int(length)
            if code == "M":
                for i in range(length):
                    curstart = self.scale.topixels(genomePosition+i, alignment.regionID)
                    curend = self.scale.topixels(genomePosition+i+1, alignment.regionID)

                    color = self.nucColors[alignment.seq[sequencePosition+i]]

                    alt = alignment.seq[sequencePosition+i]
                    ref = chromPartSeq[genomePosition+i]
                    
                    if eachNuc or alt!=ref:
                        self.svg.rect(curstart, yoffset, curend-curstart, height, fill=color, **extras)

                sequencePosition += length
                genomePosition += length
            elif code in "D":
                curstart = self.scale.topixels(genomePosition, alignment.regionID)
                curend = self.scale.topixels(genomePosition+length+1, alignment.regionID)
                self.svg.rect(curstart, yoffset, curend-curstart, height, fill=self.deletionColor, **extras)

                genomePosition += length
            elif code in "IHS":
                curstart = self.scale.topixels(genomePosition-0.5, alignment.regionID)
                curend = self.scale.topixels(genomePosition+0.5, alignment.regionID)
                self.svg.rect(curstart, yoffset, curend-curstart, height, fill=self.insertionColor, **extras)

                sequencePosition += length


    def _highlightOverlaps(self, positionCounts, yoffset, height, regionID, readID, isFlanking):
        overlapSegments = [list(i[1]) for i in itertools.groupby(sorted(positionCounts), lambda x: positionCounts[x]) if i[0] > 1]

        for segment in overlapSegments:
            start = min(segment)
            end = max(segment)

            curstart = self.scale.topixels(start, regionID)
            curend = self.scale.topixels(end, regionID)

            curColor = self.overlapColor
            # if isFlanking:
            #     curColor = "#88FF88"
            self.svg.rect(curstart, yoffset, curend-curstart, height, fill=curColor, 
                **{"class":"read", "data-readid":readID})


class Track(object):
    def __init__(self, chromPartsCollection, alignmentSets, height, width, variant, allele, thickerLines, colorCigar):
        self.chromPartsCollection = chromPartsCollection
        self.height = height
        self.width = width

        self.scale = Scale(chromPartsCollection, width)

        self.rowHeight = 5
        self.rowMargin = 1

        self.readRenderer = ReadRenderer(self.rowHeight, self.scale, self.chromPartsCollection, thickerLines, colorCigar)

        self.alignmentSets = alignmentSets

        self.svg = None
        self.rendered = None

        self.variant = variant
        self.allele = allele

        self.rows = []
        self._axis = None

        self.xmin = None
        self.xmax = None

        self.thickerLines = thickerLines


    def findRow(self, start, end, regionID):
        for currow in range(len(self.rows)):
            if self.rows[currow] is None or (start - self.rows[currow]) >= 2:
                self.rows[currow] = end
                break
        else:
            self.rows.append(end)
            currow = len(self.rows)-1

        return currow

    def getAlignments(self):
        # check which reads are overlapping (self.gstart, self.gend)
        # sorting by name makes the layout process deterministic
        regionIDsToPositions = dict((part.id, i) for i, part in enumerate(self.chromPartsCollection))

        def sortKey(alnSet):
            return (regionIDsToPositions[alnSet.getAlignments()[0].regionID], 
                    alnSet.start, alnSet.end, alnSet.name())

        return sorted(self.alignmentSets, key=sortKey)

    def dolayout(self):
        self.rows = [None]#*numRows

        self.xmin = 1e100
        self.xmax = 0

        for alignmentSet in self.getAlignments():
            # if len(alignmentSet.getAlignments()) < 2:
                # continue

            regionIDs = set([x.regionID for x in alignmentSet.getAlignments()])
            assert self.allele=="amb" or len(regionIDs)==1, alignmentSet.getAlignments()
            regionID = regionIDs.pop()

            start = self.scale.topixels(alignmentSet.start, regionID)
            end = self.scale.topixels(alignmentSet.end, regionID)

            currow = self.findRow(start, end, regionID)
            yoffset = (self.rowHeight+self.rowMargin) * currow
            alignmentSet.yoffset = yoffset

            self.xmin = min(self.xmin, self.scale.topixels(alignmentSet.start, regionID))
            self.xmax = max(self.xmax, self.scale.topixels(alignmentSet.end, regionID))

        self.height = (self.rowHeight+self.rowMargin) * len(self.rows)

    def render(self):        
        if len(self.getAlignments()) == 0:
            xmiddle = self.scale.pixelWidth / 2.0

            self.height = xmiddle/20.0

            self.svg = SVG(self.width, self.height)
            self.svg.text(xmiddle, self.height*0.05, "No reads found", size=self.height*0.9, fill="#999999")
            self.rendered = self.svg.asString()
            return self.rendered

        self.dolayout()

        self.svg = SVG(self.width, self.height)
        self.readRenderer.svg = self.svg

        alnSets = self.getAlignments()
        flankingAlignments = [alnSet for alnSet in alnSets if alnSet.parentCollection.why == "flanking"]
        nonFlankingAlignments = [alnSet for alnSet in alnSets if alnSet.parentCollection.why != "flanking"]

        for alignmentSet in flankingAlignments+nonFlankingAlignments:
            self.readRenderer.render(alignmentSet)

        lineWidth = 1 if not self.thickerLines else 3
        lineWidth = lineWidth * ((self.xmax-self.xmin)/1200.0)

        for part in self.chromPartsCollection:
            for vline in self.scale.getBreakpointPositions(part.id):
                x = self.scale.topixels(vline, part.id)
                y1 = -20
                y2 = self.height+20
                self.svg.line(x, y1, x, y2, stroke="black", **{"stroke-width":lineWidth})


        # dividers!
        for part in list(self.chromPartsCollection)[1:]:
            divWidth = self.scale.relpixels(self.scale.dividerSize)
            x = self.scale.partsToStartPixels[part.id] - divWidth
            self.svg.rect(x, self.height+40, divWidth, self.height+40, fill="#B2B2B2")
            self.svg.line(x, 0, x, self.height+40, stroke="black", **{"stroke-width":4})
            self.svg.line(x+divWidth, 0, x+divWidth, self.height+40, stroke="black", **{"stroke-width":4})

        self.svg.rect(0, self.svg.height+20, self.scale.pixelWidth, 
            self.height+40, opacity=0.0, zindex=0)
        self.rendered = str(self.svg)

        return self.rendered


class AnnotationTrack(object):
    def __init__(self, annotationSet, scale, variant, allele):
        self.chromPartsCollection = variant.chromParts(allele)
        self.annotationSet = annotationSet
        self.scale = scale
        self.height = None
        self.variant = variant
        self.allele = allele

        self._annos = None
        self.rows = [None]
        self.svg = None

        self.rowheight = 20

    def _topixels(self, gpos, segment, psegoffset):
        if segment.strand == "+":
            pos = self.scale.relpixels(gpos - segment.start) + psegoffset
        elif segment.strand == "-":
            pos = self.scale.relpixels(segment.end - gpos) + psegoffset
        return pos

    def findRow(self, start, end):
        for currow in range(len(self.rows)):
            if self.rows[currow] is None or (start - self.rows[currow]) >= 2:
                self.rows[currow] = end
                break
        else:
            self.rows.append(end)
            currow = len(self.rows)-1

        return currow

    def baseHeight(self):
        if self._annos is not None and len(self._annos) == 0:
            return 0
        return ((len(self.rows)+2) * self.rowheight) + 20

    def dolayout(self, scaleFactor, spacing):
        # coordinates are in pixels not base pairs
        self.rows = [None]

        self._annos = []
        for part in self.chromPartsCollection:
            segmentStart = self.scale.partsToStartPixels[part.id]

            for segment in variants.mergedSegments(part.segments):
                curWidth = len(segment)
                curAnnos = self.annotationSet.getAnnotations(segment.chrom, segment.start, segment.end, clip=True)
                if segment.strand == "-":
                    curAnnos = sorted(curAnnos, key=lambda x:x.end, reverse=True)

                for anno in curAnnos:
                    start = max(anno.start, segment.start)
                    end = min(anno.end, segment.end)

                    start = self._topixels(start, segment, segmentStart)
                    end = self._topixels(end, segment, segmentStart)
                    if end < start:
                        start, end = end, start
                    textLength = len(anno.label)*self.rowheight/1.0*scaleFactor*spacing
                    rowNum = self.findRow(start, end+textLength)

                    anno.coords = {}
                    anno.coords["row"] = rowNum
                    anno.coords["start"] = start
                    anno.coords["end"] = end
                    anno.coords["strand"] = anno.strand if segment.strand=="+" else utilities.switchStrand(anno.strand)
                    anno.coords["segment"] = segment
                    anno.coords["segmentStart"] = segmentStart

                    self._annos.append(anno)

                segmentStart += self.scale.relpixels(curWidth)

    def drawBox(self, start, end, segment, segmentStart, y, height, scaleFactor, color, anno):
        start = self._topixels(start, segment, segmentStart)
        end = self._topixels(end, segment, segmentStart)

        if end < start:
            start, end = end, start
            
        width = end - start

        ystart = y-((self.rowheight-height)/2.0)*scaleFactor
        self.svg.rect(start, ystart, width, height*scaleFactor, fill=color)



    def _drawGenes(self, scaleFactor):
        for anno in self._annos:
            anno.txExons # check to see if this is a gff or a bed

            color = "blue" if anno.coords["strand"] == "+" else "darkorange"

            y = ((anno.coords["row"]+1) * self.rowheight + 20) * scaleFactor
            width = anno.coords["end"] - anno.coords["start"]

            self.svg.rect(anno.coords["start"], y-((self.rowheight-2.0)/2.0)*scaleFactor, width, 2.0*scaleFactor, fill=color)     

            for txExon in anno.txExons:
                start, end = txExon
                self.drawBox(start, end, anno.coords["segment"], anno.coords["segmentStart"], y, 5, scaleFactor, color, anno)

            for cdExon in anno.cdExons:
                start, end = cdExon
                self.drawBox(start, end, anno.coords["segment"], anno.coords["segmentStart"], y, self.rowheight, scaleFactor, color, anno)

            textSize = (self.rowheight-2)*scaleFactor
            if anno.coords["end"] + len(anno.label)*textSize*0.70 > self.scale.pixelWidth:
                w = len(anno.label)*textSize*0.70
                self.svg.rect(self.scale.pixelWidth - w, y, w, self.rowheight*scaleFactor, fill="white", **{"fill-opacity":0.40})
                self.svg.text(self.scale.pixelWidth, y-((self.rowheight-1)*scaleFactor), anno.label, size=textSize, fill=color, anchor="end", **{"fill-opacity":0.70})
            else:
                self.svg.text(anno.coords["end"]+(self.rowheight/2.0), y-((self.rowheight-1)*scaleFactor), 
                    anno.label, size=textSize, anchor="start", fill=color)   

    def _drawBED(self, scaleFactor):
        for anno in self._annos:
            color = "blue" if anno.coords["strand"] == "+" else "darkorange"
            y = ((anno.coords["row"]+1) * self.rowheight + 20) * scaleFactor
            width = anno.coords["end"] - anno.coords["start"]

            self.svg.rect(anno.coords["start"], y, width, self.rowheight*scaleFactor, fill=color)
            self.svg.text(anno.coords["end"]+(self.rowheight/2.0), y-((self.rowheight-1)*scaleFactor), 
                anno.label, size=(self.rowheight-2)*scaleFactor, anchor="start", fill=color)

    def render(self, scaleFactor=1.0, spacing=1, height=None, thickerLines=False):
        self.dolayout(scaleFactor, spacing)

        self.height = self.baseHeight()*scaleFactor
        self.svg = SVG(self.scale.pixelWidth, self.height)

        # dividers! (multi-part only)
        for part in list(self.chromPartsCollection)[1:]:
            divWidth = self.scale.relpixels(self.scale.dividerSize)
            x = self.scale.partsToStartPixels[part.id] - divWidth
            self.svg.rect(x, self.height, divWidth, self.height, fill="#B2B2B2")
            self.svg.line(x, 0, x, self.height, stroke="black", **{"stroke-width":1*scaleFactor})
            self.svg.line(x+divWidth, 0, x+divWidth, self.height, stroke="black", **{"stroke-width":1*scaleFactor})

        try:
            self._drawGenes(scaleFactor)
        except Exception as e:
            self._drawBED(scaleFactor)


        for part in self.chromPartsCollection:
            for vline in self.scale.getBreakpointPositions(part.id):
                x = self.scale.topixels(vline, part.id)-scaleFactor/2.0
                y1 = 0
                y2 = self.height
                thickness = 1*scaleFactor
                if thickerLines:
                    thickness *= 2
                self.svg.line(x, y1, x, y2, stroke="black", **{"stroke-width":thickness})


