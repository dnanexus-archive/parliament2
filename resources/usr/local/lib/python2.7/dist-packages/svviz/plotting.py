try:
    from rpy2 import robjects as ro
    r = ro.r
except ImportError:
    ro = None
    r = None


def asdict(x, defaults=None):
    if defaults is None:
        defaults = {}
    if x is None:
        return defaults
    defaults.update(x)
    return defaults

def ecdf(vectors, labels=None, colors=["red", "blue", "orange", "violet", "green", "brown"],
         xlab="", ylab="cumulative fraction", main="", legendWhere="topleft", 
         lty=1, lwd=1, legendArgs=None, labelsIncludeN=True, **ecdfKwdArgs):
    """ Take a list of lists, convert them to vectors, and plots them sequentially on a CDF """

    if ro is None:
        return

    #print "MEANS:", main
    #for vector, label in zip(convertToVectors, labels):
    #    print label, numpy.mean(vector)
    
    def _expand(item):
        try:
            iter(item)
            return item
        except TypeError:
            return [item] * len(vectors)
            
    
    lty = _expand(lty)
    lwd = _expand(lwd)


    if not "xlim" in ecdfKwdArgs or ecdfKwdArgs["xlim"] is None:
        xlim = [min(min(vector) for vector in vectors if len(vector) > 0),
                max(max(vector) for vector in vectors if len(vector) > 0)]
        ecdfKwdArgs["xlim"] = xlim

    ecdfKwdArgs["xlim"] = ro.FloatVector(xlim)


    started = False
    for i, vector in enumerate(vectors):
        if len(vector) > 0:
            vector = ro.FloatVector(vector)
            ecdfKwdArgs.update({"verticals":True, "do.points":False, 
                                "col.hor":colors[(i)%len(colors)],
                                "col.vert":colors[(i)%len(colors)],
                                "lty":lty[(i)%len(lty)],
                                "lwd":lwd[(i)%len(lwd)]})
            ecdf = r.ecdf(vector)

            if not started:
                r.plot(ecdf, main=main, xlab=xlab, ylab=ylab, **ecdfKwdArgs)
                started = True
            else:
                r.plot(ecdf, add=True, **ecdfKwdArgs)

    if labels is not None:
        if labelsIncludeN:
            labelsWithN = []
            for i, label in enumerate(labels):
                labelsWithN.append(label+" (n=%d)"%len(vectors[i]))
        else:
            labelsWithN = labels
        legendArgs = asdict(legendArgs, {"cex":0.7})
        r.legend(legendWhere, legend=ro.StrVector(labelsWithN), lty=ro.IntVector(lty),
                 lwd=ro.IntVector([lwdi*2 for lwdi in lwd]), col=ro.StrVector(colors),
                 bg="white", **legendArgs)
