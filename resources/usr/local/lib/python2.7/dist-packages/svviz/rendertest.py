import pickle as pickle
import gzip
import filecmp
import json
import os
import shutil
import sys
import time

from svviz import app
from svviz import utilities

class MockArgs(object):
    def __getattr__(self, attr):
        return None


def run():
    timings = {}

    for testName in ["mei", "inv", "ins_moleculo", "ins_pacbio", "del_chr1", "translocation"]:
        print(">", testName, "<")

        exportPath = "renderTests/export_{}_new.svg".format(testName)
        originalPath = "renderTests/export_{}_original.svg".format(testName)

        d = gzip.open("renderTests/{}.pickle.gz".format(testName), "rb")
        try:
            dataHub = pickle.load(d, encoding="latin1")
        except TypeError:
            dataHub = pickle.load(d)

        dataHub.args = MockArgs()
        dataHub.args.thicker_lines = False
        dataHub.args.export = exportPath
        dataHub.args.context = 0
        
        t0 = time.time()
        app.renderSamples(dataHub)
        app.ensureExportData(dataHub)    
        app.runDirectExport(dataHub)
        t1 = time.time()
        timings[testName] = t1-t0

        no_changes = True

        if not os.path.exists(originalPath):
            print("  first time running; nothing to compare against")
            shutil.copy(exportPath, originalPath)
        else:
            if filecmp.cmp(originalPath, exportPath, shallow=False):
                print("  files identical!")
            else:
                for a, b in zip(open(originalPath).readlines(), open(exportPath).readlines()):
                    if a != b:
                        no_changes = (False, "files differ: {}".format(testName))
                        print("FILES DIFFER! First line that differs:")
                        print("Original:", a.strip())
                        print("New:     ", b.strip())
                        print("...")

                        time.sleep(3)
                        utilities.launchFile(exportPath)
                        utilities.launchFile(originalPath)

                        break


    timingsPath = "renderTests/renderTimings.json.txt"
    regenerateTimings = False
    try:
        oldTimings = json.load(open(timingsPath))
        print("{:<20}{:>20}{:>20}".format("Test Name", "Previous", "New"))
        for testName in sorted(timings):
            try:
                remark = "ok"
                if timings[testName] > oldTimings[testName] * 1.1:
                    remark = "** slower! **"
                print("{:<20}{:>19.2f}s{:>19.2f}s\t{}".format(testName, oldTimings[testName], timings[testName], remark))
            except KeyError:
                print("{:<20}{:>20}s{:>19.2f}s".format(testName, "", timings[testName]))
                regenerateTimings = True

    except IOError:
        print("unable to load previous timings...")

    if not os.path.exists(timingsPath) or regenerateTimings:
        print("overwriting previous timings...")
        json.dump(timings, open(timingsPath, "w"))
        
    return no_changes, ""