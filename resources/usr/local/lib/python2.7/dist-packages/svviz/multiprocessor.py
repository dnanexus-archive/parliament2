import multiprocessing
import sys
import time
import traceback

import signal
from array import array
try:
    from fcntl import ioctl
    import termios
except ImportError:
    pass



def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
        
    return out

# reuse process pools for multiple Multiprocessor.map() calls
# to prevent having too many interprocess communication files open
_queue = multiprocessing.Queue()
  
        
class Multiprocessor(object):
    @classmethod
    def map(cls, method, args, initArgs=None, processes=2, verbose=1, name=""):
        """
        This is the meat of things, basically a replacement for multiprocessing.pool. Subclass this class to enable
        an object-oriented approach to multiprocessing, where an object is instantiated for each pool, allowing
        local storage of unpickle-able objects, and coming with some other benefits, such as:

        - useful information about exceptions raised within the subprocesses (this is the biggest single problem with
        the plain vanilla multiprocessing library)
        - improved handling of ctrl-k termination of the multiple processes (so you usually don't have to individually
        kill -9 each sub-process)
        - some nice progress information (optionally) about the various processes as they are ongoing
        
        verbose == 1 - include information about starting and finishing each process
        verbose == 2 - print periodic updates about the status of each process
        verbose == 3 - show a full-fledged progress bar that includes information about each process
        """
    
        queue = _queue
        pool = multiprocessing.Pool(processes=processes, initializer=_map_init, initargs=[_queue])      
        # queue = multiprocessing.Queue()
        # if verbose <= 2:
        #     pool = multiprocessing.Pool(processes=processes)
        # else:
        #     pool = 

        methodname = method.__name__
        asyncResults = []
        
        for i, chunk in enumerate(chunkIt(args, processes)):
            result = pool.apply_async(_map, [cls, methodname, initArgs, chunk, i, verbose])
            result.chunkCount = i
            asyncResults.append(result)
        pool.close()

        numChunks = len(asyncResults)
        
        
        mappedValues = []

        if verbose > 2:
            progressBar = _multiProgressBar(name=name)
            # t0 = time.time()
            
        while len(asyncResults) > 0:
            for i, asyncResult in enumerate(asyncResults):
                if asyncResult.ready():
                    mappedValues.extend(asyncResult.get())
                    asyncResults.remove(asyncResult)
                    if verbose > 2:
                        progressBar.finishProcess(asyncResult.chunkCount)
                    elif verbose >= 1:
                        print("-- %i of %i done"%(numChunks-len(asyncResults), numChunks))
            
            time.sleep(0.5)

            while not queue.empty():
                status = queue.get_nowait()
                progressBar.update(status[2], status[0], status[1])

            if verbose > 2:
                progressBar.redraw()
        

        pool.join()        

        if verbose > 2:
            progressBar.finish()
        #     t1 = time.time()
        #     print "  total time elapsed:", t1-t0
        return mappedValues



def _map_init(q):
    # allow setting a multiprocessing.Queue for the _map function
    _map.q = q
    
def _map(cls, methodName, initArgs, args, chunkNum, verbose):
    """ this takes care of most of the goodies, such as instantiating the Multiprocessor
    subclass, and performing the actual 'map' activity (as well as taking care of passing
    progress information back to the main process) """
    
    t0 = time.time()
    if initArgs != None:
        instance_ = cls(*initArgs)
    else:
        instance_ = cls()
    boundMethod = getattr(instance_, methodName)
    results = []

    try:
        tlast = time.time()
        
        for i, arg in enumerate(args):
            tnow = time.time()
            
            if verbose > 1 and (i%100==0 or i%(len(args)/20+1)==0 or (tnow-tlast)>1):
                if hasattr(_map, "q"):
                    _map.q.put((i, len(args), chunkNum))
                else:
                    print(i, "of", len(args), chunkNum)

                tlast = tnow
            results.append(boundMethod(arg))
        
        t1 = time.time()
        if 0 < verbose < 3:
            print("time elapsed:", t1-t0, "chunk:", chunkNum)
        return results
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise

def formatTime(t):
    if t > 3600:
        t = "%.1fh"%(t / 3600.0)
    elif t > 60:
        t = "%.1fm"%(t / 60.0)
    else:
        t = "%.1fs"%(t)
    return t

class _multiProgressBar(object):
    """ a stupid little progress bar to keep track of multiple processes going on at once """
    def __init__(self, name=""):
        self.barsToProgress = {}

        self.t0 = time.time()
        self.timeRemaining = "--"
        self.status = "+"
        self.name = name
        self.lastRedraw = time.time()
        self.isatty = sys.stdout.isatty()

        try:
            self.handleResize(None,None)
            signal.signal(signal.SIGWINCH, self.handleResize)
            self.signal_set = True
        except:
            self.term_width = 79

    def updateTimeRemaining(self, completed, total):
        t = time.time()
        elapsed = t - self.t0

        if elapsed == 0 or completed == 0:
            return "--"
        rate = completed/float(elapsed)
        remaining = total - completed
        t_remaining = remaining / rate

        #print "\n", total, completed, elapsed, rate, remaining
        
        #return t_remaining # in seconds

        self.timeRemaining = formatTime(t_remaining)
        
    def update(self, barid, completed=None, total=None):
        if completed == None:
            completed = self.barsToProgress[barid][0]
        if total == None:
            total = self.barsToProgress[barid][1]
            
        self.barsToProgress[barid] = (completed, total)

        overallTotal = sum(x[1] for x in list(self.barsToProgress.values()))
        overallCompleted = sum(x[0] for x in list(self.barsToProgress.values()))

        self.updateTimeRemaining(overallCompleted, overallTotal)
        
    def finishProcess(self, barid):
        if not barid in self.barsToProgress:
            self.barsToProgress[barid] = (100,100)
        self.barsToProgress[barid] = (self.barsToProgress[barid][1], self.barsToProgress[barid][1])
        self.redraw()

    def finish(self):
        text = [" "]
        if len(self.name) > 0:
            text.append(self.name)
        text.append("[completed] time elapsed: {}".format(formatTime(time.time()-self.t0)))
        text = " ".join(text)
        text = text.ljust(self.term_width)
        
        sys.stderr.write(text+"\n")
        
    def redraw(self):
        if self.isatty or (time.time()-self.lastRedraw) > 30:
            overallTotal = sum(x[1] for x in list(self.barsToProgress.values()))
            overallCompleted = sum(x[0] for x in list(self.barsToProgress.values()))
            
            numBars = len(self.barsToProgress)+1
            
            barWidth = (self.term_width-40-len(self.name)) // numBars - 1

            if self.status == "+":
                self.status = " "
            else:
                self.status = "+"
                
            text = [" ", self.status]
            if len(self.name) > 0:
                text.append(self.name)

            text.append(self._getBar("total", overallCompleted, overallTotal, 25))

            text.append("left:%s"%self.timeRemaining)

            if barWidth >= 6:
                for barid in sorted(self.barsToProgress):
                    text.append(self._getBar(barid, self.barsToProgress[barid][0], self.barsToProgress[barid][1], barWidth))
            else:
                text.append("[processes=%d]"%len(self.barsToProgress))
                
            endmarker = "\n"
            if self.isatty:
                endmarker = "\r"

            sys.stderr.write(" ".join(text)+endmarker)

            self.lastRedraw = time.time()


    def _getBar(self, name, completed, total, width):
        if total == 0:
            total = 1
        name = str(name)
        if width > 20:
            # include a bar...
            barWidth = width - 9 - len(name)
            completedChars = int(barWidth * (completed/float(total)))
            uncompletedChars = barWidth - completedChars
            
            text = "%s %03.1f%% [%s%s]"%(name, completed/float(total)*100, "="*completedChars, " "*uncompletedChars)

            return text
        elif width < 11:
            text = "%s:%d%%"%(name, completed/float(total)*100)
            return text.rjust(width)            
        else:
            text = "%s : %.1f%%"%(name, completed/float(total)*100)
            return text.rjust(width)
            
    def handleResize(self, signum, frame):
        h,w=array('h', ioctl(sys.stderr,termios.TIOCGWINSZ,'\0'*8))[:2]
        self.term_width = w
        

if __name__ == "__main__":
    import time
    
    class MyMult(Multiprocessor):
        def methodASDSDG(self, arg):
            print(arg)
            time.sleep(5)
    MyMult.map(MyMult.methodASDSDG, list(range(30)), verbose=3)
