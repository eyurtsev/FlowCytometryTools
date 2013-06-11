#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy
import util
from matplotlib.widgets import Button
from matplotlib.collections import RegularPolyCollection
from matplotlib.nxutils import points_inside_poly
from matplotlib.colors import colorConverter
from dialogs import *
import glob
import fcm
from fcm import loadFCS
from gate import PolygonGate, GateKeeper, STATE_GK


#### KNOWN BUGS
### 1. I have an extra vertix somewhere [ should be fixed had to do with moving vertices first / last vertix separately. (strange matplotlib behavior)
### 2. It's too slow: coloring too many of the points
### 3. create gate -> delete gate -> create gate and cannot move vertix

class DataSet():
    def __init__(self, data, channelList):
        self.data = data
        self.channelList = channelList

    def getChannelList(self):
        return self.channelList

    def getChannelIndex(self, channel):
        return self.getChannelList().index(channel)

def main():
    fig = plt.figure()
    fig.canvas.set_window_title('FCS GUI')
    ax = fig.add_axes([0.15, 0.30, 0.7, 0.60])
    #ax = fig.add_subplot(111)
    gateKeeper = GateKeeper(ax, fig)

    ######################
    ### Create Buttons ###
    ######################

    buttonSizes = [0.05, 0.05, 0.12, 0.15]
    buttonSpacing = 0.12

    buttonList = [
            {'Label' : 'Load FCS\nFile',                  'Button Location' : buttonSizes, 'event': lambda do : openFile('Choose an FCS file', '*.fcs')},
            {'Label' : 'Load Gates\nfrom File',           'Button Location' : buttonSizes, 'event':lambda do : openFile('Choose a gates file', '*.xml')},
            {'Label' : 'Save Current\nGates to File',     'Button Location' : buttonSizes, 'event':lambda do : saveFile('Gate File (*.xml)|*.xml')},
            {'Label' : 'Polygon Gate',                    'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.setState(STATE_GK.START_DRAWING)},
            {'Label' : 'Quad Gate',                       'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.setState(STATE_GK.START_DRAWING_QUAD_GATE)},
            {'Label' : 'Delete Gate',                     'Button Location' : buttonSizes, 'event':lambda do : gateKeeper.setState(STATE_GK.DELETE_GATE)},
            {'Label' : 'Quit',                            'Button Location' : buttonSizes, 'event':lambda do : plt.close()}]

    for thisIndex, thisButton in enumerate(buttonList):
        thisButton['Button Location'][0] = 0.05 + thisIndex * buttonSpacing
        thisButton['Axes'] = plt.axes(thisButton['Button Location'])
        thisButton['Reference'] = Button(thisButton['Axes'], thisButton['Label'])
        thisButton['Reference'].on_clicked(thisButton['event'])


    numPoints = 100
    tt = numpy.linspace(0, 5, numPoints)

    x = numpy.random.random((1, numPoints)).flatten() + tt
    y = numpy.random.random((1, numPoints)).flatten() - tt
    z = numpy.sin(x) * y

    filename = glob.glob('../sample_data/*.fcs')[0]
    data = loadFCS(filename)
    #data = DataSet(data.
    #print numpy.shape(data)

    #return

    #data = DataSet(numpy.r_['0, 2', x, y, z].T, ['x', 'y', 'z'])
    gateKeeper.addData(data)
    gateKeeper.plotData()


    plt.show()

if __name__ == '__main__':
    main()
