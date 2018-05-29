import logging
import re
# from utilities import reverseComp



class Alignment(object):
    def __init__(self, name, regionID, start, end, strand, seq, cigar, score, genome_seq, score2, mapq):
        self.name = name
        self.regionID = regionID # regionID aka chromosome part ID
        self.start = start
        self.end = end
        self.strand = strand
        self.seq = seq
        self.genome_seq = genome_seq
        self.cigar = cigar
        self.score = score
        self.score2 = score2
        self.mapq = mapq


class AlignmentSet(object):
    AlnThreshold = 0.8

    def __init__(self):
        self._alignments = []
        self.evidences = {}
        self.parentCollection = None

    def is_aligned(self):
        return self.start > 0 and self.end > 0

    def __len__(self):
        # if self.start >= 0:
        return self.end - self.start + 1
        # raise Exception, "Why is the start coordinate less than 0? {} {}".format(self.start, self.end)
        # return None

    def addAlignment(self, newaln):
        self._alignments.append(newaln)
        self._alignments.sort(key=lambda x: x.start)

        self.start = min(x.start for x in self._alignments)
        self.end = max(x.end for x in self._alignments)

        if self.start < 0:
            logging.warn("Incorrect start positions: {}".format([x.start for x in self._alignments]))

    def getAlignments(self):
        return self._alignments

    def allSegmentsWellAligned(self):
        for aln in self._alignments:
            if aln.score / 2.0 < len(aln.seq) * self.AlnThreshold:
                # require matches at 80% of all positions
                return False
        return True

    def orientation(self):
        if len(self.getAlignments()) == 2:
            if (self.getAlignments()[0].start == self.getAlignments()[1].start):
                return "?"

        return "".join(aln.strand for aln in self.getAlignments())

    def name(self):
        names = set(aln.name for aln in self.getAlignments())
        if len(names) == 1:
            return names.pop()
        raise Exception("names are not consistent")


class AlignmentSetCollection(object):
    def __init__(self, name=None):
        self.name = name
        self.sets = {}
        self.choice = None
        self.why = None
        self.info = {}

    def addSet(self, newset, name):
        self.sets[name] = newset
        newset.parentCollection = self

    def choose(self, name, why=None):
        self.choice = name
        self.why = why

    def chosenSet(self):
        choice = self.choice
        if choice == "amb":
            choice = "ref"
        return self.sets[choice]

    def __getitem__(self, key):
        return self.sets[key]

def getBlastRepresentation(read):
    return _getBlastRepresentation(read.seq, read.genome_seq, read.cigar)

def _getBlastRepresentation(read_seq, genome_seq, cigar):
    pattern = re.compile('([0-9]*)([MIDNSHP=X])')

    seqout = []
    genomeout = []
    matches = []

    genomepos = 0
    seqpos = 0

    for length, code in pattern.findall(cigar):
        length = int(length)

        if code == "M":
            for i in range(length):
                g = genome_seq[genomepos]
                s = read_seq[seqpos]

                seqout.append(s)
                genomeout.append(g)

                if g == s:
                    matches.append("|")
                else:
                    matches.append("*")

                genomepos += 1
                seqpos += 1
        elif code in "D":
            for i in range(length):
                g = genome_seq[genomepos]
                genomeout.append(g)
                seqout.append("-")
                matches.append("x")
                genomepos += 1
        elif code in "IHS":
            for i in range(length):
                s = read_seq[seqpos]
                seqout.append(s)
                genomeout.append("-")
                matches.append("#")
                seqpos += 1


    return "READ:  " + "".join(seqout) + "\n" + "       " + "".join(matches) + "\n" + "GENOME:" + "".join(genomeout)


if __name__ == '__main__':
    import ssw_wrap

    class FakeRead(object): pass
    read = FakeRead()
    read.cigar = "6M"
    read.seq =        "ACCCGG"
    read.genome_seq = "ACGCGG"

    print(getBlastRepresentation(read))

    refseq = "AGGGGATTCCGATGGGAGATGAACTTATTACCAC"
    altseq = "ATTTCGATGGGTTTTTAGAGGAACTTACCAC"

    aligner = ssw_wrap.Aligner(refseq, report_cigar=True)
    aln = aligner.align(altseq)

    read.cigar = aln.cigar_string
    read.seq = altseq
    read.genome_seq = refseq[aln.ref_begin:aln.ref_end+1]


    print(repr(aln))
    print(getBlastRepresentation(read))


    """AGGGGATTTCGATGGG     AGAGGAACTTATTACCAC
            ATTTCGATGGGTTTTTAGAGGAAC   TTACCAC"""


