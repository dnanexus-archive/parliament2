import logging
import os
import pysam
import sys

from svviz import commandline
from svviz import disambiguate
from svviz import debug
from svviz import datahub
from svviz import dotplots
from svviz import export
from svviz import flanking
from svviz import insertsizes
from svviz import pairfinder
from svviz import remap
from svviz import summarystats
from svviz import track
from svviz import utilities
from svviz import variants
from svviz import vcf
from svviz import web

def checkRequirements(args):
    if not remap.check_swalign():
        print("ERROR: check that svviz is correctly installed -- the 'ssw' Smith-Waterman alignment module does not appear to be functional")
        sys.exit(1)
    if args.export:
        exportFormat = export.getExportFormat(args)
        converter = export.getExportConverter(args, exportFormat)
        if converter is None and exportFormat != "svg":
            if args.converter is not None:
                logging.error("ERROR: unable to run SVG converter '{}'. Please check that it is "
                    "installed correctly".format(args.converter))
            else:
                logging.error("ERROR: unable to export to PDF/PNG because at least one of the following "
                    "programs must be correctly installed: webkitToPDF, librsvg or inkscape")

            sys.exit(1)


def loadISDs(dataHub):
    """ Load the Insert Size Distributions """

    for sample in dataHub:
        logging.info(" > {} <".format(sample.name))
        sample.readStatistics = insertsizes.ReadStatistics(sample.bam, keepReads=dataHub.args.save_reads)

        if sample.readStatistics.orientations != "any":
            if len(sample.readStatistics.orientations) > 1:
                logging.warn("  ! multiple read pair orientations found within factor !\n"
                             "  ! of 2x of one another; if you aren't expecting your  !\n"
                             "  ! input data to contain multiple orientations, this   !\n"
                             "  ! could be a bug in the mapping software or svviz     !")
            if len(sample.readStatistics.orientations) < 1:
                logging.error("  No valid read orientations found for dataset:{}".format(sample.name))


        sample.orientations = sample.readStatistics.orientations
        if sample.orientations == "any":
            sample.singleEnded = True
        logging.info("  valid orientations: {}".format(",".join(sample.orientations) if sample.orientations!="any" else "any"))

        if sample.orientations == "any":
            searchDist = sample.readStatistics.readLengthUpperQuantile()
            alignDist = sample.readStatistics.readLengthUpperQuantile()*1.25 + dataHub.args.context
        else:
            searchDist = sample.readStatistics.meanInsertSize()+sample.readStatistics.stddevInsertSize()*2
            alignDist = sample.readStatistics.meanInsertSize()+sample.readStatistics.stddevInsertSize()*4 + dataHub.args.context
        if dataHub.args.flanks:
            searchDist += dataHub.args.context

        sample.searchDistance = int(searchDist)
        dataHub.alignDistance = max(dataHub.alignDistance, int(alignDist))

        logging.info("  Using search distance: {}".format(sample.searchDistance))

    logging.info(" Using align distance: {}".format(dataHub.alignDistance))


def loadReads(dataHub):
    readCount = 0
    readLength = 0
    maxReads = dataHub.args.max_reads
    sampleReads = dataHub.args.sample_reads
    for sample in dataHub:
        logging.info(" - {}".format(sample.name))
        sample.reads = remap.getReads(dataHub.variant, sample.bam, dataHub.args.min_mapq, dataHub.args.pair_min_mapq,
            sample.searchDistance, sample.singleEnded, dataHub.args.include_supplementary, maxReads, sampleReads)

        readCount += len(sample.reads)
        readLength += sum(len(read.seq) for read in sample.reads)
        if maxReads is not None:
            maxReads -= readCount


    logging.info(" Found {:,} reads across {} samples for a total of {:,} nt".format(readCount, len(dataHub.samples), readLength))

    if readLength > 2.5e6 or (dataHub.args.aln_quality is not None and readLength > 5e5):
        if not dataHub.args.skip_cigar and (dataHub.args.export or not dataHub.args.no_web):
            logging.warn("==== Based on the number reads (sequence nucleotides) found relevant =====\n"
                         "==== to the current variant, performance for the web browser and     =====\n"
                         "==== export may be poor; using the --skip-cigar option is            =====\n"
                         "==== recommended to reduce the number of shapes being drawn          =====")



    return readCount, readLength

def setSampleParams(dataHub):
    for sample in dataHub:
        sample.minMapq = dataHub.args.min_mapq

        if sample.singleEnded:
            sample.orientations = "any"

def runRemap(dataHub):
    for sample in dataHub:
        sample.alnCollections = remap.do_realign(dataHub, sample)

def runDisambiguation(dataHub):
    flankingRegionCollection = flanking.FlankingRegionCollection(dataHub.variant)
    for sample in dataHub:
        disambiguate.batchDisambiguate(sample.alnCollections, sample.readStatistics, sample.orientations, 
            singleEnded=sample.singleEnded, flankingRegionCollection=flankingRegionCollection,
            maxMultimappingSimilarity=dataHub.args.max_multimapping_similarity,
            alnScoreDeltaThreshold=dataHub.args.aln_score_delta)

    return disambiguate.checkMultimapping(dataHub)

def renderSamples(dataHub):
    for sample in dataHub:
        flankingReads = {"ref":[], "alt":[]}
        if dataHub.args.flanks:
            flankingReads["ref"] = [alnCollection.sets["ref"] for alnCollection in sample.alnCollections if alnCollection.why=="flanking"]
            flankingReads["alt"] = [alnCollection.sets["alt"] for alnCollection in sample.alnCollections if alnCollection.why=="flanking"]

        ref_track = track.Track(dataHub.variant.chromParts("ref"), sample.chosenSets("ref")+flankingReads["ref"], 3000, 4000, 
            variant=dataHub.variant, allele="ref", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["ref"] = ref_track

        alt_track = track.Track(dataHub.variant.chromParts("alt"), sample.chosenSets("alt")+flankingReads["alt"], 5000, 15000, 
            variant=dataHub.variant, allele="alt", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["alt"] = alt_track

        amb_track = track.Track(dataHub.variant.chromParts("ref"), sample.chosenSets("amb"), 4000, 10000,
            variant=dataHub.variant, allele="amb", thickerLines=dataHub.args.thicker_lines, colorCigar=(not dataHub.args.skip_cigar))
        sample.tracks["amb"] = amb_track

def renderAxesAndAnnotations(dataHub):
    for allele in ["alt", "ref", "amb"]:
        # TODO: store width somewhere better
        t = list(dataHub.samples.values())[0].tracks[allele]

        for name, annotationSet in dataHub.annotationSets.items():
            dataHub.alleleTracks[allele][name] = track.AnnotationTrack(annotationSet, t.scale, dataHub.variant, allele)

        axis = track.Axis(t.scale, dataHub.variant, allele)
        dataHub.alleleTracks[allele]["axis"] = axis

def ensureExportData(dataHub):
    if dataHub.trackCompositor is None:
        dataHub.trackCompositor = export.TrackCompositor(dataHub)

def runDirectExport(dataHub):
    if dataHub.args.export:
        logging.info("* Exporting views *")
        ensureExportData(dataHub)

        exportFormat = export.getExportFormat(dataHub.args)

        if dataHub.args.type == "batch":
            if not os.path.exists(dataHub.args.export):
                os.makedirs(dataHub.args.export)
            elif not os.path.isdir(dataHub.args.export):
                logging.error("In batch mode, --export must be passed as a directory, not a file: '{}'".format(dataHub.args.export))
                sys.exit(1)
            path = os.path.join(dataHub.args.export, "{}.{}".format(dataHub.variant.shortName(), exportFormat))
        else:
            path = dataHub.args.export

        exportData = dataHub.trackCompositor.render()
        filemode = "w"
        if exportFormat != "svg":
            converter = export.getExportConverter(dataHub.args, exportFormat)
            exportData = export.convertSVG(exportData, exportFormat, converter)
            filemode = "wb"
            
        with open(path, filemode) as outf:
            outf.write(exportData)

        if dataHub.args.open_exported:
            utilities.launchFile(dataHub.args.export)

        outbasepath = os.path.splitext(path)[0]
        if dataHub.args.dotplots:
            dotplotPath = outbasepath + ".dotplot.png"
            with open(dotplotPath, "wb") as dotplotFile:
                dotplotFile.write(dataHub.dotplots["ref vs ref"])

        if dataHub.args.export_insert_sizes:
            didExportISD = False

            plotInsertSizeDistributions(dataHub)
            for name, sample in dataHub.samples.items():
                if sample.insertSizePlot is not None:
                    outpath = outbasepath + ".insertsizes.{}.png".format(name)
                    with open(outpath, "w") as isdfile:
                        isdfile.write(sample.insertSizePlot)
                    didExportISD = True

            if not didExportISD:
                print("** Failed to plot the insert size distributions; please make sure the **")
                print("** rpy2 is installed, your input bam files have sufficient numbers of **")
                print("** reads (> 50,000), and that the reads are paired-ended eg Illumina  **")
                print("** and not PacBio                                                     **")

def runWebView(dataHub):
    if not dataHub.args.no_web:
        ## TODO: only prepare export SVG when needed
        ensureExportData(dataHub)
        plotInsertSizeDistributions(dataHub)

        web.dataHub = dataHub
        web.run(dataHub.args.port)

def plotInsertSizeDistributions(dataHub):
    # TODO: show only for samples with insert size distributions (ie paired end)
    if all(sample.readStatistics.hasInsertSizeDistribution() for sample in dataHub):
        plotISDs = True
        for name, sample in dataHub.samples.items():
            isd = sample.readStatistics
            sample.insertSizePlot = insertsizes.plotInsertSizeDistribution(isd, name, dataHub)
            plotISDs = plotISDs and sample.insertSizePlot
        if not plotISDs:
            for sample in dataHub:
                sample.insertSizePlot = None

def generateDotplots(dataHub):
    if dataHub.args.dotplots:
        logging.info(" * Generating dotplots *")

        dotplotPngData = dotplots.dotplot(dataHub)
        if dotplotPngData is not None:
            dataHub.dotplots["ref vs ref"] = dotplotPngData

def saveReads(dataHub, nameExtra=None):
    if dataHub.args.save_reads:
        logging.info("* Saving relevant reads *")
        for i, sample in enumerate(dataHub):
            outbam_path = dataHub.args.save_reads
            if not outbam_path.endswith(".bam"):
                outbam_path += ".bam"

            if len(dataHub.samples) > 1:
                logging.debug("Using i = {}".format(i))
                outbam_path = outbam_path.replace(".bam", ".{}.bam".format(i))

            if nameExtra is not None:
                outbam_path = outbam_path.replace(".bam", ".{}.bam".format(nameExtra))

            logging.info("  Outpath: {}".format(outbam_path))

            # print out just the reads we're interested for use later
            bam_small = pysam.Samfile(outbam_path, "wb", template=sample.bam)
            for read in sample.reads:
                bam_small.write(read)

            for read in sample.readStatistics.reads:
                bam_small.write(read)

            bam_small.close()
            sorted_path = outbam_path.replace(".bam", ".sorted")
            pysam.sort(outbam_path, sorted_path)
            pysam.index(sorted_path+".bam")

def saveState(dataHub):
    import pickle as pickle
    import gzip

    pickle.dump(dataHub, gzip.open(dataHub.args.save_state, "wb"))
    logging.warn("^"*20 + " saving state to pickle and exiting " + "^"*20)

def run(args):
    # entry point from python
    args = commandline.parseArgs(args)
    checkRequirements(args)

    dataHub = datahub.DataHub()
    dataHub.setArgs(args)

    logging.info("* Sampling reads to calculate Insert Size Distributions *")
    loadISDs(dataHub)

    if args.type == "batch":
        logging.info("* Loading variants from input VCF file *")
        dataHub.args.no_web = True
        svs = vcf.getVariants(dataHub)

        logging.info(" Loaded {} variants".format(len(svs)))
    else:
        logging.info("* Loading variant *")
        svs = [variants.getVariant(dataHub)]

    summaryStats = summarystats.Summary()
    skipped = 0
    for i, variant in enumerate(svs):
        logging.info("* Running for variant {}/{} {} *".format(i+1, len(svs), variant))
        dataHub.reset()

        dataHub.variant = variant
        setSampleParams(dataHub)

        if dataHub.args.max_size and \
                    (sum(len(part) for part in dataHub.variant.chromParts("ref")) > dataHub.args.max_size  or 
                     sum(len(part) for part in dataHub.variant.chromParts("alt")) > dataHub.args.max_size):
            logging.info("+++ Skipping variant -- event size exceeds threshold set by user ({})".format(dataHub.args.max_size))
            skipped += 1
            continue

        debug.printDebugInfo(dataHub)

        logging.info("* Loading reads and finding mates *")
        try:
            readCount, readLength = loadReads(dataHub)
        except pairfinder.TooManyReadsException:
            readCount = dataHub.args.max_reads + 1

        nameExtra = None
        if len(svs) > 1:
            nameExtra = "variant_{}".format(i)
        saveReads(dataHub, nameExtra)

        if dataHub.args.max_reads and readCount > dataHub.args.max_reads:
            logging.info("+++ Skipping variant -- number of reads ({}) exceeds threshold set by user ({})".format(
                readCount, dataHub.args.max_reads))
            skipped += 1
            continue

        logging.info("* Realigning reads *")
        runRemap(dataHub)

        logging.info("* Assigning reads to most probable alleles *")
        runDisambiguation(dataHub)

        if not dataHub.args.no_web or dataHub.args.export:
            logging.info("* Rendering tracks *")
            renderSamples(dataHub)
            renderAxesAndAnnotations(dataHub)
        generateDotplots(dataHub)

        runDirectExport(dataHub)

        summaryStats.addVariantResults(dataHub)

    summaryStats.display()
    if dataHub.args.summary is not None:
        summaryStats.saveToPath(dataHub.args.summary)

    if skipped > 0:
        logging.info("\n\nSkipped {} variants because they exceeded the --max-reads or --max-size threshold\n\n".format(skipped))
    if dataHub.args.save_state is not None:
        saveState(dataHub)
        return

    runWebView(dataHub)

    return summaryStats
    
def main():
    # entry point for shell script
    run(sys.argv)

if __name__ == '__main__':
    main()

