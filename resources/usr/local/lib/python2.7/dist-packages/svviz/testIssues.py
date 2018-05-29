import os

from svviz import app
from svviz import demo

def getData():
    tests = ["chromEnds"]

    for test in tests:
        path = "svviz-examples/{}".format(test)
        if not os.path.exists(path):
            result = demo.downloadDemo(test)
            if not result:
                raise Exception("Couldn't download the {} data.".format(test))

def run(hg19Ref):
    getData()

    bam = "svviz-examples/chromEnds/begin.chr18.bam"
    command = "svviz -t del -b {bam} {ref} chr18 30 9500 --no-web".format(ref=hg19Ref, bam=bam)
    app.run(command.split())

    bam = "svviz-examples/chromEnds/end.chr18.bam"
    command = "svviz -t del -b {bam} {ref} chr18 78001429 78127146 --no-web".format(ref=hg19Ref, bam=bam)
    app.run(command.split())


    return True, ""