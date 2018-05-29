import os
import string
import subprocess
import sys



############################ System utilities ############################
def launchFile(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))


############################ String utilities ############################
try:
    comp = str.maketrans('ATCGNatcgn','TAGCNtagcn')
except AttributeError:
    comp = string.maketrans('ATCGNatcgn','TAGCNtagcn')
    
def reverseComp(st):
    """ Returns the reverse complement of a DNA sequence; non ACGT bases will be ignored. """
    return reverseString(st).translate(comp)

def reverseString(st):
    """ Reverses a string """
    return str(st[::-1])


############################ Statistics utilities ############################

def mean(items):
    return sum(items)/float(len(items) or 1)
def stddev(items):
    if len(items) <= 1:
        return 0
    avg = mean(items)
    
    sdsq = sum([(i - avg) ** 2 for i in items])
    stddev = (sdsq / (len(items)-1)) ** .5
    
    return stddev


############################ Collections utilities ############################
def getListDefault(list_, index, default=None):
    if len(list_) <= index:
        return default

    return list_[index]


############################ Coordinates utilities ############################


def switchStrand(x):
    if x == "+":
        return "-"
    elif x == "-":
        return "+"
    
def unionLoci(loci):
    assert len(set(x.chr() for x in loci)) == 1, "Can only take union of loci on the same chromosome"
    assert len(set(x.strand() for x in loci)) == 1, "Can only take union of loci on the same strand"

    loci = sorted(loci, key=lambda l: l.start())

    union = [Locus.fromlocus(loci[0])]

    for locus in loci[1:]:
        if union[-1].end() < locus.start():
            union.append(locus)
        else:
            union[-1]._end = max(union[-1].end(), locus.end())

    return union


class Locus:
    """ An all-purpose genomic locus class; use for any kind of datum that can be represented
    with a chromosome, start, end, and strand """
    __switch = {'+':'-', '-':'+'}

    def __init__(self, chr_, start, end, strand):
        """
        :param chr: chromosome name (string)
        :param strand: '+' or '-' (or '.' for an ambidexterous locus)
        :param start: start coordinate of the locus
        :param end: coord of the last nucleotide (inclusive) """
        coords = [start,end]
        coords.sort()
        # this method for assigning chromosome should help avoid storage of
        # redundant strings.
        self._chr = chr_
        self._strand = strand
        self._start = int(coords[0])
        self._end = int(coords[1])

        if self._start < 0:
            raise Exception("Locus start coordinate cannot be negative: {}".format(start))
        
    @classmethod
    def fromlocus(class_, otherLocus):
        return class_(otherLocus.chr(), otherLocus.start(), otherLocus.end(), otherLocus.strand())

    def chr(self):
        """ Returns the chromosome """
        return self._chr
    
    def start(self):
        """ returns the smallest coordinate """
        return self._start
    
    def end(self):
        """ returns the biggest coordinate """
        return self._end 
    
    def len(self):
        """ :returns: the length of the locus from start to end, inclusive

        The length of a Locus instance ``loc1`` can be gotten by using either ``loc1.len()`` or
        ``len(loc1)`` """
        return self._end - self._start + 1
    
    def __len__(self):
        return self.len()
    
    def getAntisenseLocus(self):
        """ Returns a copy of the locus with the strand flipped """
        if self._strand=='.':
            return self
        else:
            return Locus(self._chr,self._start,self._end,self.__switch[self._strand])

    def strand(self):
        """ :returns: the strand of the locus ie ``+`` or ``-`` """
        return self._strand
    
    def overlaps(self,otherLocus):
        """ Returns ``True`` if this locus overlaps ``otherLocus`` """
        if self.chr()!=otherLocus.chr():
            return False
        elif not(self._strand=='.' or 
                 otherLocus.strand()=='.' or 
                 self.strand()==otherLocus.strand()): return False
        elif self.start() > otherLocus.end() or otherLocus.start() > self.end():
            return False
        else:
            return True
        
    def overlapsAntisense(self,otherLocus):
        """ same as overlaps, but considers the opposite strand """
        return self.getAntisenseLocus().overlaps(otherLocus)

    def __hash__(self):
        """ This method allows Locus instances to be entered as keys into a dict, and is integral to
        speedy access to loci through the LocusCollection. Note that multiple loci can share the same hash
        (eg they can be on opposite DNA strands) as long as ``__eq__`` can distinguish between them """
        return self._start + self._end
    
    def __eq__(self,other):
        """ Used to check if two loci are distinct from one another; this method ensures that hash conflicts
        are resolved appropriately when loci are entered into dictionaries """
        if self.__class__ != other.__class__: return False
        if self.chr()!=other.chr(): return False
        if self.start()!=other.start(): return False
        if self.end()!=other.end(): return False
        if self.strand()!=other.strand(): return False
        return True
    
    # def __ne__(self,other): return not(self.__eq__(other))
    
    def __repr__(self):
        return "Locus%s"%str(self)

    def __str__(self):
        return "(" + self._chr +":" + str(self.start()) + "-" + str(self.end()) + self._strand + ")"

if __name__ == '__main__':
    # loci = [Locus("chr1", 10, 20, "+"),
    #         Locus("chr1", 18, 22, "+"),
    #         Locus("chr1", 22, 25, "+"),
    #         Locus("chr1", 27, 30, "+"),
    #         Locus("chr1", 28, 31, "+"),
    #         Locus("chr1", 35, 40, "+"),
    #         Locus("chr1", 42, 45, "+"),
    #         Locus("chr1", 43, 44, "+")]

    # print unionLoci(loci)

    from svviz.variants import Segment, mergedSegments
    segments = [Segment("chr100", 1,3, "+", 0),
                Segment("chr100", 5, 9, "+", 1), 
                Segment("chr100", 11, 15, "+", 2), 
                Segment("chr100", 17, 19, "+", 3), 
                Segment("chr100", 21, 31, "+", 4),
                Segment("chr100", 33, 34, "+", 5)]

    print(segments)
    print(mergedSegments(segments))

