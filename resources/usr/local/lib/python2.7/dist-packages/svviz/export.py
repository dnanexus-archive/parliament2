import collections
import logging
import os
import subprocess
import sys
import tempfile
import time


class TrackCompositor(object):
    def __init__(self, dataHub, title=None):
    # def __init__(self, width, title=None): 
        self.dataHub = dataHub
        self.sections = collections.OrderedDict()
        self.width = 1200
        self.title = title
        self.descriptions = []

        self.marginTopBottom = 20
        self.sectionLabelHeight = 32
        self.betweenSectionHeight = 30
        self.trackLabelHeight = 20

        self._fromDataHub()

    def _fromDataHub(self):
        if self.title is None:
            self.title = str(self.dataHub.variant)

        for longAlleleName in ["Alternate Allele", "Reference Allele"]:
            allele = longAlleleName[:3].lower()

            sampleNames = list(self.dataHub.samples.keys())
            tracks = [sample.tracks[allele] for sample in self.dataHub]

            self.addTracks(longAlleleName, sampleNames, tracks, allele)

    def getBounds(self, tracks, allele):
        """ calculate left and right bounds for the allele; this is based on the variant segments
        as well as the positions of the reads (we want to be able to see all the breakpoints as 
        well as all the reads) """

        scale = tracks[0].scale

        # bail if there are multiple sections; could do this more nicely
        if len(self.dataHub.variant.chromParts(allele).parts) > 1:
            return 0, scale.pixelWidth

        segments = list(self.dataHub.variant.chromParts(allele))[0].segments
        alleleLength = len(list(self.dataHub.variant.chromParts(allele))[0])

        if self.dataHub.args.context>0:
            begin = scale.topixels(len(segments[0])-self.dataHub.args.context)
            width = scale.topixels(sum(len(s) for s in segments[:-1])+self.dataHub.args.context) - begin
            return begin, width

        axisMin = max(0, scale.topixels(len(segments[0])-100))
        axisMax = scale.topixels(min(alleleLength-len(segments[-1])+100, alleleLength))

        for track in tracks:
            track.render()
        xmin = [track.xmin for track in tracks if track.xmin is not None]
        xmin = min(xmin) if len(xmin) > 0 else 0
        xmin = min(axisMin, xmin)

        xmax = [track.xmax for track in tracks if track.xmax is not None]
        xmax = max(xmax) if len(xmax) > 0 else 500
        xmax = max(axisMax, xmax)

        width = 500
        if xmin is not None:
            width = xmax - xmin
            xmin -= width * 0.05
            xmin = max(0, xmin)
            width *= 1.1
            width = min(width, xmin+scale.topixels(alleleLength))
        return xmin, width

    def addTracks(self, section, names, tracks, allele):
        alleleTracks = self.dataHub.alleleTracks[allele]

        for track in tracks:
            track.render()
        xmin, width = self.getBounds(tracks, allele)

        hasTrackWithReads = False

        for track, name in zip(tracks, names):
            if len(track.alignmentSets) == 0:
                height = 20
                viewbox = '0 0 {width} {height}" preserveAspectRatio="xMinYMin'.format(width=track.width, height=track.height)
            else:
                hasTrackWithReads = True
                # this is for proportional scaling                
                # height = float(track.height+40) * self.width / width
                # preserveAspectRatio="xMinYMin"
                height = float(track.height+40)/2.0
                preserveAspectRatio="none"

                viewbox = '{xmin} -20 {width} {height}" preserveAspectRatio="{par}'.format(xmin=xmin, 
                    width=width, height=track.height+40, par=preserveAspectRatio)

            self.addTrackSVG(section, name, track.svg.asString("export"), height=height, viewbox=viewbox)

        # if hasTrackWithReads:
        if True:
            scaleFactor = float(width) / self.width
            size = 1.0
            if self.dataHub.args.thicker_lines:
                size *= 2.0

            for name, track in alleleTracks.items():
                # this is awkward: baseHeight() and imageHeight are used
                # for Axis tracks but not Annotation tracks
                imageHeight = width * (track.baseHeight()/float(self.width))
                track.render(scaleFactor=scaleFactor, height=imageHeight,  
                    thickerLines=self.dataHub.args.thicker_lines)
                height = track.height/scaleFactor

                viewbox = '{xmin} 0 {width} {height}" preserveAspectRatio="{par}'.format(xmin=xmin, 
                    width=width, height=track.height,
                    par="none")
                svg = track.svg.asString("export")

                self.addTrackSVG(section, name, svg, height=track.baseHeight(),#height, 
                    viewbox=viewbox)



    def addTrackSVG(self, section, name, tracksvg, viewbox=None, height=100):
        if not section in self.sections:
            self.sections[section] = collections.OrderedDict()
        self.sections[section][name] = {"svg":tracksvg,
                                        "viewbox":viewbox,
                                        "height": height
                                       }

    def _svgText(self, x, y, text, height, bold=False, anchor=None):
        extras = ""
        if bold:
            extras += ' font-weight="bold"'
        if anchor:
            extras += ' anchor="{}"'.format(anchor)
        svg = '<svg x="{x}" y="{y}"><text x="0" y="{padded}" font-size="{textHeight}" font-family="Helvetica" {extras}>{text}</text></svg>'.format(x=x, y=y, 
            padded=height, textHeight=(height-2), text=text, extras=extras)
        return svg

    def renderCountsTable(self, modTracks, ystart, fontsize=18):
        charWidth = fontsize/2
        ystart += 5
        counts = self.dataHub.getCounts()
        columns = ["Sample", "Alt", "Ref", "Amb"]

        columnWidths = []
        longestRowHeader = max(max(len(x) for x in counts), len(columns[0]))
        columnWidths.append(longestRowHeader*charWidth)
        columnWidths.extend([7*charWidth]*3)

        rows = [columns]
        for sample, curcounts in counts.items():
            rows.append([sample, curcounts["alt"], curcounts["ref"], curcounts["amb"]])

        for i, row in enumerate(rows):
            xstart = 10
            for j, value in enumerate(row):
                width = columnWidths[j]
                if j == 0:
                    # row header
                    modTracks.append(self._svgText(xstart, ystart, value, fontsize, bold=True, anchor="start"))
                    xstart += width
                else:
                    xstart += width
                    modTracks.append(self._svgText(xstart, ystart, value, fontsize, bold=i==0, anchor="end"))
            ystart += fontsize * 1.25

        return ystart + 10
            # self.descriptions.append("{}: {} {} {}".format(name, curcounts["alt"], curcounts["ref"], curcounts["amb"]))

    def render(self):
        modTracks = []
        curX = 0
        curY = self.marginTopBottom

        if self.title is not None:
            header = self._svgText(curX+10, curY, self.title, self.sectionLabelHeight+5, bold=True)
            modTracks.append(header)
            curY += self.sectionLabelHeight+10

        curY = self.renderCountsTable(modTracks, curY)

        # for description in self.descriptions:
        #     header = self._svgText(curX+20, curY, description, self.trackLabelHeight)
        #     modTracks.append(header)
        #     curY += self.trackLabelHeight+5

        for i, sectionName in enumerate(self.sections):
            section = self.sections[sectionName]

            if i > 0:
                curY += self.betweenSectionHeight

            label = self._svgText(curX+10, curY, sectionName, self.sectionLabelHeight)
            modTracks.append(label)
            curY += self.sectionLabelHeight

            for trackName in section:
                trackInfo = section[trackName]

                if trackName != "axis":
                    label = self._svgText(curX+10, curY, trackName, self.trackLabelHeight)
                    modTracks.append(label)
                    curY += self.sectionLabelHeight

                extra = 'svg x="{}" y="{}" width="{}" height="{}"'.format(curX, curY, self.width, trackInfo["height"])
                if trackInfo["viewbox"] is not None:
                    extra += ' viewBox="{}"'.format(trackInfo["viewbox"])
                mod = trackInfo["svg"].replace("svg", extra, 1)
                modTracks.append(mod)

                curY += trackInfo["height"]

        curY += self.marginTopBottom

        composite = ['<?xml version="1.0" encoding="utf-8" ?><svg  xmlns="http://www.w3.org/2000/svg" ' + \
                     'xmlns:xlink="http://www.w3.org/1999/xlink" width="{}" height="{}">'.format(self.width, curY)] + \
                     modTracks + ["</svg>"]
        return "\n".join(composite)


def getExportFormat(args):
    formats = [None, "png", "pdf", "svg"]
    if args.type == "batch" or args.format is not None:
        exportFormat = args.format
        if exportFormat is None:
            exportFormat = "pdf"
    else:
        exportFormat = args.export.partition(".")
        if len(exportFormat[2]) > 0:
            exportFormat = exportFormat[2]
            if exportFormat not in formats:
                logging.warn("= File suffix {} not recognized; exporting as .svg =".format(exportFormat))
                exportFormat = "svg"
        else:
            exportFormat = "svg"

    exportFormat = exportFormat.lower()
    return exportFormat

def getExportConverter(args, exportFormat):
    if args.converter == "webkittopdf" and exportFormat=="png":
        logging.error("webkitToPDF does not support export to PNG; use librsvg or inkscape instead, or "
            "export to PDF")
        sys.exit(1)

    if exportFormat == "png" and args.converter is None:
        return "librsvg"

    if args.converter == "rsvg-convert":
        return "librsvg"

    if args.converter in [None, "webkittopdf"]:
        if checkWebkitToPDF():
            return "webkittopdf"

    if args.converter in [None, "librsvg"]:
        if checkRSVGConvert():
            return "librsvg"

    if args.converter in [None, "inkscape"]:
        if checkInkscape():
            return "inkscape"

    return None



def checkWebkitToPDF():
    try:
        subprocess.check_call("webkitToPDF", stderr=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def checkRSVGConvert():
    try:
        subprocess.check_call("rsvg-convert -v", stdout=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def checkInkscape():
    try:
        subprocess.check_call("inkscape --version", stdout=subprocess.PIPE, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def convertSVG(insvg, outformat, converter):
    outdir = tempfile.mkdtemp()
    inpath = "{}/original.svg".format(outdir)
    infile = open(inpath, "w")
    infile.write(insvg)
    infile.flush()
    infile.close()

    outpath = "{}/converted.{}".format(outdir, outformat)

    if converter == "webkittopdf":
        exportData = _convertSVG_webkitToPDF(inpath, outpath, outformat)
    elif converter == "librsvg":
        exportData = _convertSVG_rsvg_convert(inpath, outpath, outformat)
    elif converter == "inkscape":
        exportData = _convertSVG_inkscape(inpath, outpath, outformat)

    return exportData

def _convertSVG_webkitToPDF(inpath, outpath, outformat):
    if outformat.lower() != "pdf":
        return None

    try:
        cmd = "webkitToPDF {} {}".format(inpath, outpath)
        subprocess.check_call(cmd, shell=True)#, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return None

    return open(outpath, "rb").read()

def _convertSVG_inkscape(inpath, outpath, outformat):
    options = ""
    outformat = outformat.lower()
    if outformat == "png":
        options = "--export-dpi 150 --export-background white"

    try:
        subprocess.check_call("inkscape {} {} --export-{}={}".format(options, inpath, outformat, outpath), 
            shell=True)
    except subprocess.CalledProcessError as e:
        print("EXPORT ERROR:", str(e))

    return open(outpath, "rb").read()


def _convertSVG_rsvg_convert(inpath, outpath, outformat):
    options = ""
    outformat = outformat.lower()
    if outformat == "png":
        options = "-a --background-color white"

    try:
        subprocess.check_call("rsvg-convert -f {} {} -o {} {}".format(outformat, options, outpath, inpath), shell=True)
    except subprocess.CalledProcessError as e:
        print("EXPORT ERROR:", str(e))

    return open(outpath, "rb").read()


# def test():
#     base = """  <svg><rect x="10" y="10" height="100" width="100" style="stroke:#ffff00; stroke-width:3; fill: #0000ff"/><text x="25" y="25" fill="blue">{}</text></svg>"""
#     svgs = [base.format("track {}".format(i)) for i in range(5)]

#     tc = TrackCompositor(200, 600)
#     for i, svg in enumerate(svgs):
#         tc.addTrack(svg, i, viewbox="0 0 110 110")

#     outf = open("temp.svg", "w")
#     outf.write(tc.render())
#     outf.flush()
#     outf.close()

#     pdfPath = convertSVGToPDF("temp.svg")
#     subprocess.check_call("open {}".format(pdfPath), shell=True)

# if __name__ == '__main__':
#     test()

#     import sys
#     print(canConvertSVGToPDF(), file=sys.stderr)