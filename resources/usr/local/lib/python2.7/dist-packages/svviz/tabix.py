import logging
import os
import pysam
import subprocess


class AnnotationError(Exception):
    pass

def ensureIndexed(bedPath, preset="bed", trySorting=True):
    if not bedPath.endswith(".gz"):
        if not os.path.exists(bedPath+".gz"):
            logging.info("bgzf compressing {}".format(bedPath))
            pysam.tabix_compress(bedPath, bedPath+".gz")
            if not os.path.exists(bedPath+".gz"):
                raise Exception("Failed to create compress {preset} file for {file}; make sure the {preset} file is "
                    "sorted and the directory is writeable".format(preset=preset, file=bedPath))
        bedPath += ".gz"
    if not os.path.exists(bedPath+".tbi"):
        logging.info("creating tabix index for {}".format(bedPath))
        pysam.tabix_index(bedPath, preset=preset)
        if not os.path.exists(bedPath+".tbi"):
            raise Exception("Failed to create tabix index file for {file}; make sure the {preset} file is "
                "sorted and the directory is writeable".format(preset=preset, file=bedPath))

    line = next(pysam.Tabixfile(bedPath).fetch())
    if len(line.strip().split("\t")) < 6 and preset == "bed":
        raise AnnotationError("BED files need to have at least 6 (tab-delimited) fields (including "
            "chrom, start, end, name, score, strand; score is unused)")
    if len(line.strip().split("\t")) < 9 and preset == "gff":
        raise AnnotationError("GFF/GTF files need to have at least 9 tab-delimited fields")

    return bedPath


# def sortFile(uncompressedPath, preset):
#     if preset == "bed":
#         fields = {"chrom":0, "start":1, "end":2}
#     elif preset == "gff":
#         fields = {"chrom":0, "start":3, "end":4}

#     sortCommand = "sort -k{chrom}V -k{start}n -k{end}n".format(**fields)

#     tabixCommand = "{sort} {path} | bgzip > {path}.gz".format(sort=sortCommand, path=uncompressedPath)

#     logging.info("Trying to sort input annotation file with command:")
#     logging.info("  {}".format(tabixCommand))

#     subprocess.check_call(tabixCommand, shell=True)
