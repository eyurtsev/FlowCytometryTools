#!/usr/bin/env python
import matplotlib.pyplot as plt
import util
import matplotlib.pyplot as plt
import numpy
import util
from matplotlib.widgets import Button, Cursor
from matplotlib.collections import RegularPolyCollection
from matplotlib.nxutils import points_inside_poly
from matplotlib.colors import colorConverter
from dialogs import *
#import os
#import wx
#import wx.lib.agw.multidirdialog as MDD


###################
# DEFINITIONS 
###################

def euclid_distance((x1, y1), (x2, y2)):
    return numpy.sqrt((x1-x2)**2 + (y1 - y2)**2)

class MOUSE:
    leftClick = 1
    rightClick = 3

class STYLE:
    InactivePolygonGate = {'color' : 'black', 'linestyle' : 'solid', 'fill' : False}
    ActivePolygonGate = {'color' : 'red', 'fill' : False}

    #SuggestToActivateGate = {'color' : 'red', 'fill' : 'gray', 'alpha' : 0.4}
    TemporaryPolygonGateBorderLine = {'color' : 'black'}
    PolygonGateBorderLine = {'color' : 'None',  'linestyle' : 'None', 'marker':'s', 'mfc':'r', 'alpha':0.6}

    InactiveQuadGate = {'color' : 'black', 'linewidth' : 1}
    ActiveQuadGate   = {'color' : 'red', 'linewidth' : 2}
    InactiveQuadGateCenter = {'color' : 'black', 'marker' : 's', 'markersize' : 8}
    ActiveQuadGateCenter   = {'color' : 'red', 'marker' : 's', 'markersize' : 8}

    DATUM_IN_COLOR = colorConverter.to_rgba('red')
    DATUM_OUT_COLOR = colorConverter.to_rgba('gray')

class STATE_GK:
    START_DRAWING = 'Start Drawing Gate'
    START_DRAWING_QUAD_GATE = 'Start Drawing Quad Gate'
    KEEP_DRAWING = 'Creating a gate'
    WAITING = 'Waiting'
    QUIT = 'Quitting'
    DELETE_GATE = 'Delete Active Gate'

class Filter(object):
    """An object representing a gatable region"""

    def __init__(self, vert=None, channels=None, name=None, gateKeeper=None):
        """
        vert = vertices of gating region
        channels = indices of channels to gate on.
        """
        self.vert = vert
        self.channels = list(channels)
        self.press = None
        self.active = False

        if name is None:
            self.name = "N/A"
        else:
            self.name = name

        self.setGateKeeper(gateKeeper)
        ### Used while drawing the gate ###

        ### Used for GUI ###
        self.fig = gateKeeper.fig
        self.ax = gateKeeper.ax
        self.connect()

    def __repr__(self):
        return "%s(%s,%s,%s)".format(self.__class__, str(self.vert), str(self.channels), self.name)
    def __str__(self):
        return "<%s (%s) on %s>".format(self.__class__, self.name, str(self.channels))


    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state

    def isActive(self):
        return self.getState() == 'Active'


    #################
    ## GUI Control 
    #################

    def connect(self):
        'connect to all the events we need'
        print('connecting gate to events.')
        self.cidpress   = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion  = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidpick    = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cidkey     = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.fig.canvas.mpl_disconnect(self.cidpress)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidpick)
        self.fig.canvas.mpl_disconnect(self.cidkey)

    def on_motion(self, event):
        print 'on_motion: not defined'

    def on_release(self, event):
        'on release we reset the press data'
        print 'on_release: not defined'

    def on_pick(self, event):
        util.raiseNotDefined()

    def on_press(self, event):
        print 'on_press: not defined'

    def on_key(self, event):
        print 'on_key: not defined'

    def getArtist(self):
        return self.artist

    def contains(self, event):
        contains, attrd = self.getArtist().contains(event)
        return contains

    def getGateKeeper(self): return self.gateKeeper
    def setGateKeeper(self, gateKeeper): self.gateKeeper = gateKeeper

class QuadGate(Filter):
    """ Defines a polygon gate. """
    def __init__(self, vert=None, channels=None, name=None, gateKeeper=None):
        Filter.__init__(self, vert, channels, name, gateKeeper)
        self.createArtist()
        self.setState('Active')
        #self.setState('Creating Gate')
        #self.lineToProposedvertixix = None
        #self.temporaryBorderLineList = []

    def createArtist(self):
        artistList = []
        vert = self.vert

        self.vline = self.ax.axvline(x=vert[0], **STYLE.ActiveQuadGate)
        self.hline = self.ax.axhline(y=vert[1], **STYLE.ActiveQuadGate)
        self.center = plt.Line2D([vert[0]], [vert[1]], picker=10, **STYLE.ActiveQuadGateCenter)
        self.ax.add_artist(self.center)
        self.artistList = [self.vline, self.hline, self.center]
        plt.draw()

    def on_press(self, event):
        if event.inaxes != self.ax: return
        if self.getState() == 'Active':
            if not self.contains(event):
                self.inactivate()
            else:
                self.setState('Moving Vertix')

    def on_pick(self, event):
        pass

    def on_motion(self, event):
        if self.getState() == 'Moving Vertix':
            self.vline.set_xdata((event.xdata, event.xdata))
            self.hline.set_ydata((event.ydata, event.ydata))
            self.center.set_xdata([event.xdata])
            self.center.set_ydata([event.ydata])
            plt.draw()

    def on_release(self, event):
        if self.getState() == 'Moving Vertix':
            self.vline.set_xdata((event.xdata, event.xdata))
            self.hline.set_ydata((event.ydata, event.ydata))
            self.center.set_xdata([event.xdata])
            self.center.set_ydata([event.ydata])
            self.setState('Active')
            plt.draw()

    def inactivate(self):
        self.setState('Inactive')
        self.vline.update(STYLE.InactiveQuadGate)
        self.hline.update(STYLE.InactiveQuadGate)
        self.center.update(STYLE.InactiveQuadGateCenter)
        self.fig.canvas.draw()

    def activate(self):
        self.setState('Active')
        self.vline.update (STYLE.ActiveQuadGate)
        self.hline.update (STYLE.ActiveQuadGate)
        self.center.update(STYLE.ActiveQuadGateCenter)
        self.fig.canvas.draw()

    def getArtist(self):
        print 'here'
        return self.center


    def removeArtist(self):
        for artist in self.artistList:
            artist.remove()

    def removeGate(self):
        self.disconnect()
        self.removeArtist()
        self.fig.canvas.draw()
        self.gateKeeper.removeGate(self)

class PolygonGate(Filter):
    """ Defines a polygon gate. """
    def __init__(self, vert=None, channels=None, name=None, gateKeeper=None):
        Filter.__init__(self, vert, channels, name, gateKeeper)
        self.setState('Creating Gate')
        self.vertices = []
        self.lineToProposedVertix = None
        self.temporaryBorderLineList = []

    def getArtist(self): return self.poly

    def getClosestVertix(self, currentCoordinate):
        """ Get closest vertix. """
        #for thisVertix in self.getVertices()
        distancesList = [(euclid_distance(currentCoordinate, thisVertix), thisIndex, thisVertix) for thisIndex, thisVertix in enumerate(self.getVertices())]
        distancesList.sort(key = lambda x : x[0])
        distance, closestVerticIndex, closestVertixPosition = distancesList[0]
        print 'Computing Closest'
        print distancesList[0]
        print closestVerticIndex
        return distance, closestVerticIndex, closestVertixPosition

    def addVertixToGrowingPolygon(self, vertix):
        self.vertices.append(vertix)
        if len(self.vertices) > 1:
            lastLine = zip(self.vertices[-2], self.vertices[-1])
            self.temporaryBorderLineList.append(plt.Line2D(lastLine[0], lastLine[1], **STYLE.TemporaryPolygonGateBorderLine))
            self.ax.add_artist(self.temporaryBorderLineList[-1])

    def finishDrawingPolygon(self, vertix):
        self.vertices.append(vertix)

        ## Remove artists used for helping with gate creation
        self.lineToProposedVertix.remove()
        for temporaryBorderLine in self.temporaryBorderLineList: temporaryBorderLine.remove()

        # Create the artist
        self.createArtist()

    def createArtist(self):
        ## Create polygon
        self.poly = plt.Polygon(self.vertices, picker=15, **STYLE.ActivePolygonGate)
        self.ax.add_artist(self.poly)

        ## Create PolygonBorder
        x, y = zip(*self.poly.xy)
        self.polygonBorder = plt.Line2D(x[:-1], y[:-1], **STYLE.PolygonGateBorderLine)
        self.ax.add_artist(self.polygonBorder)

        self.adjust_border()

    def removeArtist(self):
        self.poly.remove()
        self.polygonBorder.remove()

    def getVertices(self, transAxes=False):
        """ Return vertices in axis coordinates """
        ## TODO Fix a bug here to make sure selected points are close in axis space rather than data space.
        if transAxes:
            xy = self.poly.get_xy()
            inv = self.ax.transAxes.inverse()
            return inv.transform(xy)
        else:
            return self.poly.get_xy()

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        print 'mouse press'
        print '--- Mouse ---'*3
        print self.getState()
        print '-'
        if event.inaxes != self.ax: return

        #if self.getState() == 'Inactive' and self.gateKeeper.getState() not in [STATE_GK.START_DRAWING, STATE_GK.KEEP_DRAWING]:
            #if self.contains(event):
                #self.activate()
        if self.getState() == 'Creating Gate':
            newVertix = (event.xdata, event.ydata)
            if event.button == MOUSE.leftClick:
                self.addVertixToGrowingPolygon(newVertix)
            if event.button == MOUSE.rightClick:
                self.finishDrawingPolygon(newVertix)
                self.setState('Active')
                self.getGateKeeper().setState(STATE_GK.WAITING)
        elif self.getState() == 'Active':
            if self.contains(event):
                print('contains the event.')
                self.info = self.getClosestVertix((event.xdata, event.ydata))
                self.setState('Moving Vertix')
            else:
                self.inactivate()

        self.fig.canvas.draw()

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        print '-'*80
        print self.getState()

        if self.getState() <> 'Creating Gate':
            print self.poly.contains(event)

        if self.getState() == 'Inactive':
            return
        elif self.getState() == 'Creating Gate':
            print 'mouse moving'
            lastVertix = self.vertices[-1]
            potentialVertixPosition = (event.xdata, event.ydata)
            print potentialVertixPosition
            print lastVertix
            line_xydata = zip(lastVertix, potentialVertixPosition)

            if self.lineToProposedVertix is None:
                self.lineToProposedVertix = plt.Line2D(line_xydata[0], line_xydata[1])
                self.ax.add_artist(self.lineToProposedVertix)
            else:
                self.lineToProposedVertix.set_xdata(line_xydata[0])
                self.lineToProposedVertix.set_ydata(line_xydata[1])
            self.fig.canvas.draw()
        elif self.getState() == 'Moving Vertix':
            print self.info
            closestVertixIndex = self.info[1]

            numVertices = len(self.getVertices())

            xy = self.poly.get_xy()
            if closestVertixIndex == 0 or closestVertixIndex == numVertices-1: # TODO needed because of unintuitive matplotlib behavior. first and last vertix to be the same
                xy[0] = (event.xdata, event.ydata)
                xy[-1] = (event.xdata, event.ydata)
            else:
                xy[closestVertixIndex] = (event.xdata, event.ydata)

            self.poly.set_xy(xy)
            self.adjust_border()

    def adjust_border(self):
        """ Method that implements relevant changes when the polygon is changed. """
        xy = self.poly.get_xy()

        self.polygonBorder.set_xdata(xy[:, 0])
        self.polygonBorder.set_ydata(xy[:, 1])

        self.gateKeeper.grayoutAllPoints()
        self.gateKeeper.highlightPointsInsideGate(self)

        self.fig.canvas.draw()

    def on_release(self, event):
        #util.raiseNotDefined()
        'on release we reset the press data'
        if self.getState() == 'Moving Vertix':
            self.setState('Active')

    def on_pick(self, event):
        """ Picking vertices. """
        return

    def on_key(self, event):
        if event.key == 'i':
            self.inactivate()
        elif event.key == 'a':
            self.activate()
        elif event.key == 'd': # Delete gate if the gate is active
            if self.getState() == 'Active':
                self.removeGate()

    def removeGate(self):
        self.disconnect()
        self.removeArtist()
        self.fig.canvas.draw()
        self.gateKeeper.removeGate(self)

    def inactivate(self):
        self.setState('Inactive')
        self.poly.update(STYLE.InactivePolygonGate)
        self.polygonBorder.set_visible(False)
        self.poly.figure.canvas.draw()

    def activate(self):
        self.setState('Active')
        self.poly.update(STYLE.ActivePolygonGate)
        self.polygonBorder.set_visible(True)
        self.poly.figure.canvas.draw()

    def setVisibility(self, visible=True):
        ## TODO implemented a quick fix Very likely to be buggy
        self.poly.set_visible(visible)
        self.polygonBorder.set_visible(visible)
        if visible==True:
            if self.getState() == 'Active':
                self.activate()
            elif self.getState() == 'Inactive':
                self.activate()
        plt.draw()

class GateKeeper():
    """ This will maintain a list of all the active gates. """
    def __init__(self, ax, fig, gateList=None):
        if gateList is not None: self.gateList = gateList
        else: self.gateList = []
        self.data = None
        self.collection = None
        self.fig =  fig
        self.ax = ax
        self.setState(STATE_GK.WAITING)
        self.connect()
        self.current_channels = [0, 1]

        # For Quad Gate
        self.cursorWidget = None

    def connect(self):
        #self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion  = self.fig.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.cidpress   = self.fig.canvas.mpl_connect('button_press_event',  self.mouse_press_callback)
        self.cidkey     = self.fig.canvas.mpl_connect('key_press_event',  self.on_key)
        self.cidpick    = self.fig.canvas.mpl_connect('pick_event', self.on_pick)

    def disconnect(self):
        'disconnect all the stored connection ids'
        ## TODO Define disconnect event properly
        plt.gcf().canvas.mpl_disconnect(self.cidpress)
        #plt.gcf().canvas.mpl_disconnect(self.cidrelease)
        plt.gcf().canvas.mpl_disconnect(self.cidmotion)
        plt.gcf().canvas.mpl_disconnect(self.cidpick)
        plt.gcf().canvas.mpl_disconnect(self.cidkey)

    def on_release(self):
        return

    def motion_notify_callback(self, event):
        """ Motion events. """
        print 'Gate Keeper state: ', self.getState()

        if self.getState() == STATE_GK.START_DRAWING_QUAD_GATE:
            if self.cursorWidget == None:
                self.cursorWidget = Cursor(self.ax)


        return

    def mouse_press_callback(self, event):
        """ Button press events. """
        print '-'*80
        print 'Gate Keeper state: ', self.getState()
        if self.getState() == STATE_GK.START_DRAWING:
            print 'creating a gate'

            poly = PolygonGate(vert=None, channels=self.current_channels, name=None, gateKeeper=self)
            self.addGate(poly)
            self.getGateList()[-1].on_press(event)
            self.setState(STATE_GK.KEEP_DRAWING)
        elif self.getState() == STATE_GK.WAITING:
            print 'Selecting gates...'
            # Quick and dirty code here. Can optimize

            ## Choose gate
            if len(self.getGateList()) > 0:
                activeGateList = [thisGate for thisGate in self.getGateList() if thisGate.contains(event)]

                for thisGate in self.getGateList():
                    if thisGate.contains(event):
                        if not thisGate.isActive():
                            thisGate.activate()
                            self.grayoutAllPoints()
                            self.highlightPointsInsideGate(thisGate)

                            for gateToInactivate in activeGateList:
                                if gateToInactivate is not thisGate:
                                    gateToInactivate.inactivate()

                        break

                # Now let's put the active gate on the top layer...
                self.getGateList().remove(thisGate)
                self.getGateList().insert(0, thisGate)
        elif self.getState() == STATE_GK.START_DRAWING_QUAD_GATE:
            quadGate = QuadGate(vert=(event.xdata, event.ydata), channels=self.current_channels, name="N/A", gateKeeper=self)
            self.addGate(quadGate)
            del self.cursorWidget
            self.cursorWidget = None
            self.setState(STATE_GK.WAITING)

    def changeAxis(self, event):
        if event.artist == self.xlabelArtist:
            self.current_channels[0] = selectOption('Select channel for x axis', self.data.channels)

        elif event.artist == self.ylabelArtist:
            self.current_channels[1] = selectOption('Select channel for y axis', self.data.channels)

        self.showVisibleGates()
        self.plotData()

    def showVisibleGates(self):
        for thisGate in self.getGateList():
            print thisGate.channels
            print self.current_channels
            if thisGate.channels == self.current_channels:
                print 'here'
                thisGate.setVisibility(True)
            else:
                print 'beer'
                thisGate.setVisibility(False)
        plt.draw()

    def on_pick(self, event):
        """ Event picker """
        if event.artist == self.xlabelArtist or event.artist == self.ylabelArtist:
            ### In case we want to change the axis
            self.changeAxis(event)

    def on_key(self, event):
        if event.key == 'c':
            self.setState(STATE_GK.START_DRAWING)

    def addGate(self, gate):
        """ Adds the current gate to the gate list. """
        self.getGateList().append(gate)

    def removeGate(self, gate):
        self.getGateList().remove(gate)
        del gate

    def getGateList(self):
        return self.gateList

    def getActivePolygonGate(self):
        for thisGate in self.getGateList():
            if thisGate.isActive():
                return thisGate

    def getState(self):
        return self.state

    def setState(self, state):
        if state == STATE_GK.DELETE_GATE:
            activeGate = self.getActivePolygonGate()
            if activeGate:
                activeGate.removeGate()
            state = STATE_GK.WAITING

        self.ax.set_title(state)
        self.fig.canvas.draw()
        self.state = state

    def addData(self, data):
        if self.data is not None: util.raiseNotDefined()
        self.data = data

    def plotData(self):
        numData = numpy.shape((self.data))[0]
        facecolors = [STYLE.DATUM_OUT_COLOR for d in range(numData)]

        index1, index2 = self.current_channels

        self.dataxy = self.data[:1000, [index1, index2]]
        ax = self.ax

        if self.collection is not None:
            self.collection.remove()


        self.collection = RegularPolyCollection(ax.figure.dpi, 6, sizes=(10,), alpha=0.8, facecolors=facecolors, offsets = self.dataxy, transOffset = ax.transData)
        self.ax.add_collection(self.collection)

        #self.ax.set_ylim(-10, 10)
        #self.ax.set_xlim(-10, 10)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        xlabel = self.data.channels[index1]
        ylabel = self.data.channels[index2]

        self.xlabelArtist = self.ax.set_xlabel(xlabel, picker=5)
        self.ylabelArtist = self.ax.set_ylabel(ylabel, picker=5)
        plt.draw()

    def grayoutAllPoints(self):
        if self.data is None: return

        numDataPoints = len(self.dataxy)

        facecolors = self.collection.get_facecolors()
        for i in range(numDataPoints):
            facecolors[i] = STYLE.DATUM_OUT_COLOR
        self.fig.canvas.draw()

    def highlightPointsInsideGate(self, gate):
        """ Locates the points inside the given polygon vertices. """
        if self.data is None: return

        numDataPoints = len(self.dataxy)

        print 'Data points length'
        print numDataPoints

        if isinstance(gate, PolygonGate):
            facecolors = self.collection.get_facecolors()
            inPointsIndexes = numpy.nonzero(points_inside_poly(self.dataxy, gate.getVertices()))[0]
            for i in inPointsIndexes:
                facecolors[i] = STYLE.DATUM_IN_COLOR

        self.fig.canvas.draw()
