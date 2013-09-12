#!/usr/bin/env python
"""
A place holder for a command line script that will plot a given
FCS file(s).

DO NOT USE At the moment.

author: Eugene Yurtsev
date: 2013-08-08
"""

import matplotlib.pyplot as plt
import fcm.graphics as graph
import glob, csv, os, argparse
import util
import numpy
import datetime, time

from Utilities import graph, util
from argparse import RawTextHelpFormatter

import time

def plotFCSFiles(fileList, gateCoordinates, numPoints=1000, save=False):
    """
    Plots FCS files.

    Assumptions:
        Assumes that the FCS files belong to a single plate.

    Input:
        fileList : list
    """
    if len(fileList) == 0:
        raise Exception('Found no files matching regular expression : {}'.format(options.filename))
    if len(fileList) == 1:
        fileAnalyzed = FCS_TO_CSV(fileList[0], gateCoordinates)
        fileAnalyzed.plot(numPoints=numPoints)
        if save:
            graph.saveFigure(fileList[0], tictoc=True, formats=['.jpg'])
        plt.show()
    else:
        fig = plt.gcf()
        ax_main = plt.gca()
        plt.subplots_adjust(hspace=0,wspace=0)#, right=0.9)#, right=0.75)
        xtick_labels = numpy.arange(12)+1
        ytick_labels = ['ABCDEFGH'[i] for i in range(8)]

        numRows = 8
        numCols = 12

        plt.xticks(numpy.linspace(0, 1, numCols+1)+1/2.0/(numCols+1.0), xtick_labels)
        plt.yticks(numpy.linspace(1, 0, 9)-1/2.0/(numRows+1.0), ytick_labels)
        plt.xlim(0, 1)
        plt.ylim(0, 1)

        for filename in fileList:
            fileAnalyzed = FCS_TO_CSV(filename, gateCoordinates)
            row = ord(fileAnalyzed.info['WELL ID'][0])-ord('A')
            col = int(fileAnalyzed.info['WELL ID'][1:])
            #print fileAnalyzed.info['WELL ID']
            #print row, col
            loc = col+row*12
            #print loc
            thisAxes = fig.add_subplot(numRows, numCols, col+row*12)
            plt.ylim(0, 2*10**5)
            plt.xlim(0, 2*10**5)

            fileAnalyzed.plot(annotate=False, numPoints=numPoints, s=1)
        mtitle='EID: {EID:n}, PID: {SAMPLE ID:n}\nName: {Plate Name}, Date: {Date}, End Time: {End Time}'.format(**fileAnalyzed.getInfo())
        plt.suptitle(mtitle)

        if save:
            graph.saveFigure(fileAnalyzed.info['Plate Name'], tictoc=True, formats=['.jpg'])
        plt.show()


def main(options):
    #print 'Options passed: {}'.format(options)
    print os.curdir
    fileList = options.filename

    if fileList is None:
        fileList = acquireFiles()
        #print('Found {} FCS files.'.format(len(fileList)))
        #print('Detected files: {}'.format(fileList))

    gateCoordinates = options.gate_coordinates

    if options.plot:
        plotFCSFiles(fileList, gateCoordinates, numPoints=options.num_points, save=options.save)

    elif options.analyze:
        print 'analyzing'
        print 'csv output {}'.format(options.csv_filename)
        with open(options.csv_filename, 'w') as foutput:
            tic = time.time()
            fileAnalyzed = FCS_TO_CSV(fileList[0], gateCoordinates)
            headerString = fileAnalyzed.getOutputHeader()
            dw = csv.DictWriter(foutput, delimiter=',', fieldnames=headerString, extrasaction='ignore') # extrasaction ignores additional fields in the dictionary
            dw.writeheader()
            dw.writerow(fileAnalyzed.getOutputDict())
            if len(fileList) > 1:
                for index, filename in enumerate(fileList[1:]):
                    try:
                        fileAnalyzed = FCS_TO_CSV(filename, gateCoordinates)
                        dw.writerow(fileAnalyzed.getOutputDict())
                    except:
                        print('Could not analyze file: {}'.format(filename))

                    if index % 10 == 0:
                        print('{:.2f}% complete'.format(index * 1.0 / len(fileList)*100.0))
            toc = time.time()

            print('This script took {} seconds to run.'.format(toc-tic))

def parseInput():
    """
    Examples of use:
    To plot all the fcs files in the directory sample_data:
		python batch_fcs.py -f sample_data/*.fcs -p',
    To plot all the fcs files in the directory sample_data and save to file:
		python batch_fcs.py -f sample_data/*.fcs -p -s',
    To analyze and save all the fcs files in the directory sample_data to file:
		python batch_fcs.py -f sample_data/*.fcs -a -o output.csv',
    To analyze and save all the fcs files within a selectable subdirectory (brings out an interface):
		python batch_fcs.py -a -o output.csv',
    """
    epilog = parseInput.__doc__

    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=RawTextHelpFormatter)

    parser.add_argument("-f", "--files", dest="filename", help="fcs file(s) to open", metavar="FILE", nargs='+', default=None)

    parser.add_argument("-g", "--gate-type", dest="gate_type", default="Quad Gate", help="options: Quad Gate")
    parser.add_argument("-c", "--gate-coordinates", dest="gate_coordinates", nargs='+', type=float, help="coordinate gate")

    parser.add_argument("-p", "--plot", dest="plot", action="store_true", help="plot fcs file(s)")
    parser.add_argument("-s", "--save plot", dest="save", action="store_true", help="save fcs plot")
    parser.add_argument("-a", "--analyze", dest="analyze", action="store_true", help="output to a csv file")
    parser.add_argument("-o", "--csv", dest="csv_filename", help="filename for csv output", default='temp.csv')

    parser.add_argument("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    return parser.parse_args()

if __name__ == '__main__':
    pArgs = parseInput()
    main(pArgs)
