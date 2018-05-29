import logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def printDebugInfo(dataHub):
    if dataHub.args.verbose > 3:
        info = []

        info.append("="*80)

        for allele in ["ref", "alt"]:
            for part in dataHub.variant.chromParts(allele):
                info.append(str(part))
            info.append("")
        logging.debug("\n".join(info))

    if dataHub.args.verbose > 9:
        info = []

        info.append("="*80)

        for allele in ["ref", "alt"]:
            for part in dataHub.variant.chromParts(allele):
                info.append(str(part.getSeq()))
            info.append("")
        logging.debug("\n".join(info))
