import collections
import logging
import numpy
import time

def scoreAlignmentSetCollection(alnCollection, isd, minInsertSizeScore=0, expectedOrientations="any", singleEnded=False,
                                flankingRegionCollection=None, maxMultimappingSimilarity=0.9):
    for name, alignmentSet in alnCollection.sets.items():
        if not singleEnded:
            alignmentSet.evidences["insertSizeScore"] = isd.scoreInsertSize(len(alignmentSet))
        else:
            alignmentSet.evidences["insertSizeScore"] = None

        alignmentSet.evidences["alignmentScore"] = sum(aln.score for aln in alignmentSet.getAlignments())
        alignmentSet.evidences["orientation"] = alignmentSet.orientation()

        alignmentSet.evidences["valid"] = (True, )

        regionIDs = set()
        multimapping = 0

        for read in alignmentSet.getAlignments():
            regionIDs.add(read.regionID)
            if read.score2 is not None:
                scoreDiff = read.score2/float(read.score)
                multimapping = max(scoreDiff, multimapping)

        if multimapping > maxMultimappingSimilarity:            
            alignmentSet.evidences["multimapping"] = multimapping
        alnCollection.info["multimapping"] = max(multimapping, alnCollection.info.get("multimapping", 0))

        if len(regionIDs) == 1:
            alignmentSet.evidences["flanking"] = False
            if flankingRegionCollection is not None and flankingRegionCollection.isFlanking(alignmentSet, name):
                alignmentSet.evidences["flanking"] = True
        else:
            alignmentSet.evidences["valid"] = (False, "multiRegion")


        if not singleEnded:
            if alignmentSet.evidences["insertSizeScore"] <= minInsertSizeScore:
                alignmentSet.evidences["valid"] = (False, "insertSizeScore")
            if not checkOrientation(alignmentSet.evidences["orientation"], expectedOrientations):
                alignmentSet.evidences["valid"] = (False, "orientation")
        if not alignmentSet.allSegmentsWellAligned():
            alignmentSet.evidences["valid"] = (False, "alignmentScore")

def checkOrientation(orientation, expectedOrientations):
    if expectedOrientations in ["any", None]:
        return True
    if orientation in expectedOrientations:
        return True
    return False

def disambiguate(alnCollection, insertSizeLogLikelihoodCutoff=1.0, singleEnded=False,
    alnScoreDeltaThreshold=2):
    # TODO: the cutoffs used below are somewhat arbitrary

    def choose(which, why):
        alnCollection.choose(which, why)
        return which

    refAlnScore = alnCollection["ref"].evidences["alignmentScore"]
    altAlnScore = alnCollection["alt"].evidences["alignmentScore"]

    altValid = alnCollection["alt"].evidences["valid"][0]
    refValid = alnCollection["ref"].evidences["valid"][0]

    # check the validity of the alignment sets (see scoreAlignmentSetCollection())
    if "multimapping" in alnCollection["alt"].evidences:
        if altAlnScore / float(refAlnScore) > 0.66:
            return choose("amb", "multimapping")

    if "multimapping" in alnCollection["ref"].evidences:
        if refAlnScore / float(altAlnScore) > 0.66:
            return choose("amb", "multimapping")

    alnCollection.info["multimapping"] = 0

    if altValid and not refValid:
        return choose("alt", alnCollection["ref"].evidences["valid"][1])
    if refValid and not altValid:
        return choose("ref", alnCollection["alt"].evidences["valid"][1])
    if not refValid and not altValid:
        return choose("amb", str(alnCollection["ref"].evidences["valid"][1])+"_"+str(alnCollection["alt"].evidences["valid"][1]))

    if isinstance(alnScoreDeltaThreshold, float):
        readLength = sum([len(aln.seq) for aln in alnCollection["ref"].getAlignments()])
        alnScoreDeltaThreshold = alnScoreDeltaThreshold * readLength

    if altAlnScore-alnScoreDeltaThreshold > refAlnScore:
        return choose("alt", "alignmentScore")
    if refAlnScore-alnScoreDeltaThreshold > altAlnScore:
        return choose("ref", "alignmentScore")

    if not singleEnded:
        logRatio = numpy.log10(alnCollection["alt"].evidences["insertSizeScore"] / alnCollection["ref"].evidences["insertSizeScore"])
        if logRatio > insertSizeLogLikelihoodCutoff:
            return choose("alt", "insertSizeScore")
        if logRatio < -insertSizeLogLikelihoodCutoff:
            return choose("ref", "insertSizeScore")

    if alnCollection["alt"].evidences["flanking"] and alnCollection["ref"].evidences["flanking"]:
        return choose("amb", "flanking")

    return choose("amb", "same_scores")

def batchDisambiguate(alnCollections, isd, expectedOrientations, singleEnded=False, flankingRegionCollection=None,
    maxMultimappingSimilarity=0.9, alnScoreDeltaThreshold=2):
    t0 = time.time()

    for alnCollection in alnCollections:
        scoreAlignmentSetCollection(alnCollection, isd, 0, expectedOrientations, singleEnded=singleEnded,
            flankingRegionCollection=flankingRegionCollection, maxMultimappingSimilarity=maxMultimappingSimilarity)

    for alnCollection in alnCollections:
        disambiguate(alnCollection, singleEnded=singleEnded, alnScoreDeltaThreshold=alnScoreDeltaThreshold)

    t1 = time.time()
    logging.info(" Time for disambiguation: {:.2f}s".format(t1-t0))


def checkMultimapping(dataHub):
    alreadyWarned = False

    # only warn if the --max-multimapping-similarity command-line setting
    # hasn't been adjusted down substantially
    if dataHub.args.max_multimapping_similarity < 0.9:
        return

    for sample in dataHub:
        counts = collections.defaultdict(int)

        for alnCollection in sample.alnCollections:
            score = alnCollection.info.get("multimapping", 0)
            if score > 0.99:
                counts[1.0] += 1
            elif score >= 0.95:
                counts[0.95] += 1
            elif score >= 0.90:
                counts[0.9] += 1

            if score >= dataHub.args.max_multimapping_similarity:
                counts["similar"] += 1

            counts["total"] += 1

        if (counts[1.0] + counts[0.9] > counts["total"] * 0.1) or (counts[1.0] + counts[0.9] > 100):
            if not alreadyWarned:
                logging.warn("\n   " + "*"*100 + "\n"
                    "   Found a substantial number of reads that could map to multiple locations \n"
                    "   within the same allele; please consider using the --dotplots option to check \n"
                    "   repetitiveness within these genomic regions: or use the \n"
                    "   --max-multimapping-similarity option to adjust how many of these reads \n"
                    "   are marked as ambiguous\n")
            logging.warn("   Sample = {}".format(sample.name))
            logging.warn("   {} align equally well to 2+ locations\n".format(counts[1.0]))
            logging.warn("   {} align nearly equally well to 2+ locations\n".format(counts[0.95]))
            logging.warn("   {} align similarly to 2+ locations\n".format(counts[0.9]))

            alreadyWarned = True

    if alreadyWarned:
        logging.warn("   "+ "*"*100 + "\n")
