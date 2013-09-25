#!/usr/bin/env python
import pylab as pl
from matplotlib.collections import RegularPolyCollection
#from matplotlib.nxutils import points_inside_poly
#from matplotlib.colors import colorConverter
from util import call_wrapper
from GoreUtilities import util
import numpy
from util import debugging_print
from manager_states import STATE_GK
from FlowCytometryTools.core import gates as base_gates

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
    PolygonGateBorderLine = {'color' : 'black',  'linestyle' : 'None', 'marker':'s', 'mfc':'r', 'alpha':0.6}

    InactiveQuadGate = {'color' : 'black', 'linewidth' : 1}
    ActiveQuadGate   = {'color' : 'red', 'linewidth' : 2}
    InactiveQuadGateCenter = {'color' : 'black', 'marker' : 's', 'markersize' : 8}
    ActiveQuadGateCenter   = {'color' : 'red', 'marker' : 's', 'markersize' : 8}

class PlottableGate():
    """ For use with GUI """
    def __init__(self, gate_manager):
        """
        """
        self.gate_manager = gate_manager

        ##
        # GUI Attributes
        self.fig = gate_manager.fig
        self.ax = gate_manager.ax

    def set_state(self, state):
        self.state = state

    @property
    def active(self):
        return self.state == 'Active'

    def connect(self, event_list):
        mpl_connect_dict = {
                'mouse press' : ('button_press_event', self.on_press),
                'mouse release' :  ('button_release_event', self.on_release),
                'mouse motion' : ('motion_notify_event', self.on_mouse_motion),
                'pick event' : ('pick_event', self.on_mouse_pick),
                'keyboard press' : ('key_press_event', self.on_keyboard_press)
            }

        self.mpl_cid = {}

        for event in event_list:
            event_type, bound_function = mpl_connect_dict[event]
            self.mpl_cid[event] = self.fig.canvas.mpl_connect(event_type, bound_function)

    def disconnect(self):
        """ disconnects all the stored connection ids """
        for cid in self.mpl_cid:
            self.fig.canvas.mpl_disconnect(self.mpl_cid[cid])

    def on_mouse_motion(self, event):
        util.raiseNotDefined()

    def on_release(self, event):
        util.raiseNotDefined()

    def on_mouse_pick(self, event):
        util.raiseNotDefined()

    def on_press(self, event):
        util.raiseNotDefined()

    def on_keyboard_press(self, event):
        util.raiseNotDefined()

    def get_control_artist(self):
        util.raiseNotDefined()

    def contains(self, event):
        if self.channels != self.gate_manager.current_channels:
            return False
        contains, attrd = self.get_control_artist().contains(event)
        return contains

    def set_visible(self, visible=True):
        """
        Method is responsible for showing or hiding the gate.
        Useful when the x/y axis change.
        """
        for artist in self.artist_list:
            artist.set_visible(visible)

        if visible:
            if self.state == 'Active':
                self.activate()
            elif self.state == 'Inactive':
                self.inactivate()
        self.fig.canvas.draw()

    def remove_gate(self):
        """ Removes the gate properly. """
        self.disconnect()

        # Remove artists
        for artist in self.artist_list:
            artist.remove()

        self.fig.canvas.draw()
        self.gate_manager.remove_gate(self)

class QuadGate(PlottableGate, base_gates.QuadGate):
    """ Defines a polygon gate. """
    def __init__(self, vert, channels, region, name=None, gate_manager=None):
        #base_gates.Gate.__init__(self, vert=vert, channels=channels, region=region, name=name)
        PlottableGate.__init__(self, gate_manager)
        base_gates.QuadGate.__init__(self, vert, channels, region, name)
        self.create_artist()
        self.set_state('Active')
        self.connect(['mouse press', 'mouse release', 'mouse motion', 'keyboard press'])

    #@call_wrapper
    def create_artist(self):
        vert = self.vert
        self.vline = self.ax.axvline(x=vert[0], **STYLE.ActiveQuadGate)
        self.hline = self.ax.axhline(y=vert[1], **STYLE.ActiveQuadGate)
        self.center = pl.Line2D([vert[0]], [vert[1]], **STYLE.ActiveQuadGateCenter)
        self.ax.add_artist(self.center)
        self.artist_list = [self.vline, self.hline, self.center]
        self.fig.canvas.draw()

    #@call_wrapper
    def on_press(self, event):
        debugging_print('Quad Gate. Mouse motion: ')
        debugging_print(self)
        if event.inaxes != self.ax: return

        if self.state == 'Active':
            if not self.contains(event):
                self.inactivate()
            else:
                print ("CONTAINS EVENT")
                self.state = 'Moving Vertix'
                print 'new state = {}'.format(self.state)

    #@call_wrapper
    def on_mouse_motion(self, event):
        debugging_print('Quad Gate. Mouse motion: ')
        debugging_print(self)
        #debugging_print(self.state)
        if self.state == 'Moving Vertix':
            self.vert = (event.xdata, event.ydata)
            self.draw()

    #@call_wrapper
    def on_release(self, event):
        if self.state == 'Moving Vertix':
            self.vline.set_xdata((event.xdata, event.xdata))
            self.hline.set_ydata((event.ydata, event.ydata))
            self.center.set_xdata([event.xdata])
            self.center.set_ydata([event.ydata])
            self.set_state('Active')
            self.fig.canvas.draw()

    #@call_wrapper
    def inactivate(self):
        self.set_state('Inactive')
        self.vline.update(STYLE.InactiveQuadGate)
        self.hline.update(STYLE.InactiveQuadGate)
        self.center.update(STYLE.InactiveQuadGateCenter)
        self.fig.canvas.draw()

    def get_control_artist(self):
        return self.center

    #@call_wrapper
    def activate(self):
        self.set_state('Active')
        self.vline.update(STYLE.ActiveQuadGate)
        self.hline.update(STYLE.ActiveQuadGate)
        self.center.update(STYLE.ActiveQuadGateCenter)
        self.fig.canvas.draw()

    def draw(self):
        xdata = self.vert[0]
        ydata = self.vert[1]
        self.vline.set_xdata((xdata, xdata))
        self.hline.set_ydata((ydata, ydata))
        self.center.set_xdata([xdata])
        self.center.set_ydata([ydata])
        self.fig.canvas.draw()

class PolygonDrawer(PlottableGate):
    """ Used to create a polygon gate by drawing it on the axis. """
    def __init__(self, channels, gate_manager):
        PlottableGate.__init__(self, gate_manager)

        # Connect gate to GUI events
        self.connect(['mouse press', 'mouse motion'])

        # Initialization sequence
        self.lineToProposedVertix = None
        self.temporaryBorderLineList = []

        self.vert = []
        self.channels = channels

    def add_vertix_to_growing_polygon(self, vertix):
        self.vert.append(vertix)
        if len(self.vert) > 1:
            lastLine = zip(self.vert[-2], self.vert[-1])
            self.temporaryBorderLineList.append(pl.Line2D(lastLine[0], lastLine[1], **STYLE.TemporaryPolygonGateBorderLine))
            self.ax.add_artist(self.temporaryBorderLineList[-1])

    def finish_drawing_polygon(self, vertix):
        self.vert.append(vertix)

        ## Remove artists used for helping with gate creation
        self.lineToProposedVertix.remove()

        for temporaryBorderLine in self.temporaryBorderLineList:
            temporaryBorderLine.remove()

        # instantiate polygon gate and add to gate manager
        pg = PolygonGate(vert=self.vert, channels=self.channels,
                region='in', name=None, gate_manager=self.gate_manager)

        self.gate_manager.add_gate(pg)
        self.gate_manager.set_state(STATE_GK.WAITING)
        self.disconnect()

    def on_press(self, event):
        if event.inaxes != self.ax: return

        newVertix = (event.xdata, event.ydata)

        if event.button == MOUSE.leftClick:
            self.add_vertix_to_growing_polygon(newVertix)

        if event.button == MOUSE.rightClick:
            self.finish_drawing_polygon(newVertix)
            self.gate_manager.set_state(STATE_GK.WAITING)

        self.fig.canvas.draw()

    def on_mouse_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        lastVertix = self.vert[-1]
        potentialVertixPosition = (event.xdata, event.ydata)
        line_xydata = zip(lastVertix, potentialVertixPosition)

        if self.lineToProposedVertix is None:
            self.lineToProposedVertix = pl.Line2D(line_xydata[0], line_xydata[1])
            self.ax.add_artist(self.lineToProposedVertix)
        else:
            self.lineToProposedVertix.set_xdata(line_xydata[0])
            self.lineToProposedVertix.set_ydata(line_xydata[1])
        self.fig.canvas.draw()

class PolygonGate(PlottableGate, base_gates.PolyGate):
    """ Defines a polygon gate. """
    def __init__(self, vert, channels, region=None, name=None, gate_manager=None):
        PlottableGate.__init__(self, gate_manager)
        base_gates.PolyGate.__init__(self, vert, channels, region, name)

        # Connect gate to GUI events
        self.set_state('Active')
        self.connect(['mouse press', 'mouse release', 'mouse motion', 'keyboard press'])
        self.create_artist()

    def create_artist(self):
        ## Create polygon
        self.poly = pl.Polygon(self.vert, **STYLE.ActivePolygonGate)
        self.ax.add_artist(self.poly)

        ## Create PolygonBorder
        x, y = zip(*self.poly.xy)
        self.polygonBorder = pl.Line2D(x[:-1], y[:-1], **STYLE.PolygonGateBorderLine)
        self.ax.add_artist(self.polygonBorder)

        self.artist_list = [self.poly, self.polygonBorder]
        self.adjust_border()

    def get_control_artist(self):
        return self.poly

    def get_vertices(self, transAxes=False):
        """ Return vertices in axis coordinates """
        ## TODO Fix a bug here to make sure selected points are close in axis space rather than data space.
        if transAxes:
            xy = self.poly.get_xy()
            inv = self.ax.transAxes.inverse()
            return inv.transform(xy)
        else:
            return self.poly.get_xy()

    def get_closest_vertix(self, currentCoordinate):
        """ Get closest vertix. """
        #for thisVertix in self.get_vertices()
        distancesList = [(euclid_distance(currentCoordinate, thisVertix), thisIndex, thisVertix) for thisIndex, thisVertix in enumerate(self.get_vertices())]
        distancesList.sort(key = lambda x : x[0])
        distance, closestVerticIndex, closestVertixPosition = distancesList[0]
        debugging_print('Computing Closest')
        debugging_print(distancesList[0])
        debugging_print(closestVerticIndex)
        return distance, closestVerticIndex, closestVertixPosition

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.ax: return

        if self.state == 'Active':
            if self.contains(event):
                debugging_print('contains the event.')
                self.info = self.get_closest_vertix((event.xdata, event.ydata))
                self.set_state('Moving Vertix')

        self.fig.canvas.draw()

    def on_mouse_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        debugging_print(self)
        if self.state == 'Inactive':
            return
        elif self.state == 'Moving Vertix':
            closestVertixIndex = self.info[1]

            numVertices = len(self.get_vertices())
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

        self.fig.canvas.draw()

    def on_release(self, event):
        #util.raiseNotDefined()
        'on release we reset the press data'
        if self.state == 'Moving Vertix':
            self.set_state('Active')

    def on_keyboard_press(self, event):
        if event.key == 'i':
            self.inactivate()
        elif event.key == 'a':
            self.activate()
        elif event.key == 'd': # Delete gate if the gate is active
            if self.state == 'Active':
                self.remove_gate()

    def inactivate(self):
        self.set_state('Inactive')
        self.poly.update(STYLE.InactivePolygonGate)
        self.polygonBorder.set_visible(False)
        self.poly.figure.canvas.draw()

    def activate(self):
        self.set_state('Active')
        self.poly.update(STYLE.ActivePolygonGate)
        self.polygonBorder.set_visible(True)
        self.poly.figure.canvas.draw()

