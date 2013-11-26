from matplotlib.widgets import  RectangleSelector, Cursor, AxesWidget
from pylab import *
import pylab as pl
from numpy import random
import numpy

class MOUSE:
    LEFT_CLICK = 1
    RIGHT_CLICK = 3


class STYLE:
    InactivePolyGate = {'color' : 'black', 'linestyle' : 'solid', 'fill' : False}
    ActivePolyGate = {'color' : 'red', 'fill' : False}

    #SuggestToActivateGate = {'color' : 'red', 'fill' : 'gray', 'alpha' : 0.4}
    TemporaryPolyGateBorderLine = {'color' : 'black'}
    PolyGateBorderLine = {'color' : 'black',  'linestyle' : 'None', 'marker':'s', 'mfc':'r', 'alpha':0.6}

    InactiveQuadGate = {'color' : 'black', 'linewidth' : 1}
    ActiveQuadGate   = {'color' : 'red', 'linewidth' : 2}
    InactiveQuadGateCenter = {'color' : 'black', 'marker' : 's', 'markersize' : 8}
    ActiveQuadGateCenter   = {'color' : 'red', 'marker' : 's', 'markersize' : 8}

class Vertex(AxesWidget):
    def __init__(self, coordinates, ax=None, update_notify_callback=None):
        AxesWidget.__init__(self, ax)
        self.update_notify_callback = update_notify_callback
        self.selected = False
        self.coordinates = coordinates
        self.create_artist()
        self.connect_event('pick_event', lambda event : self.pick(event))
        self.connect_event('motion_notify_event', lambda event : self.motion_notify_event(event))
        #self.connect_event('button_press_event', lambda event : self.mouse_button_press(event))
        self.connect_event('button_release_event', lambda event : self.mouse_button_release(event))

    def create_artist(self):
        self.artist = pl.Line2D([self.coordinates[0]], [self.coordinates[1]], picker=10, marker='s', color='r', ms=10)
        self.ax.add_artist(self.artist)

    def ignore(self, event):
        """ Ignores events. """
        if hasattr(event, 'inaxes'):
            if event.inaxes != self.ax:
                return True
        else:
            return False

    def pick(self, event):
        if self.artist != event.artist:
            return
        if self.ignore(event):
            return
        self.selected = not self.selected

    def mouse_button_release(self, event):
        if self.ignore(event):
            return
        if self.selected:
            self.selected = False

    def motion_notify_event(self, event):
        if self.selected:
            self.update_position(event.xdata, event.ydata)
            self._update()

    def update_position(self, xdata, ydata):
        self.coordinates = xdata, ydata
        self.artist.set_xdata([xdata])
        self.artist.set_ydata([ydata])

    def _update(self):
        if self.update_notify_callback is not None:
            self.update_notify_callback(self)
        pl.gcf().canvas.draw_idle()


class PolyGate(AxesWidget):
    def __init__(self, verts, ax=None):
        AxesWidget.__init__(self, ax)
        update_notify_callback = lambda vertex : self.update_position(vertex)

        self.poly = pl.Polygon(verts, color='k', fill=False)
        self.ax.add_artist(self.poly)
        self.vertex_list = [Vertex(vert, ax, update_notify_callback) for vert in verts]

    def update_position(self, vertex):
        xy = [vertex.coordinates for vertex in self.vertex_list]
        self.poly.set_xy(xy)

class DoubleVertex(AxesWidget):
    def __init__(self, verts, ax=None):
        AxesWidget.__init__(self, ax)
        update_notify_callback = lambda vertex : self.update_position(vertex)
        self.vertex1 = Vertex(verts, ax, update_notify_callback=update_notify_callback)
        verts2 = list(verts)
        verts2[0] = verts[0] + 2.4
        self.vertex2 = Vertex(verts2, ax, update_notify_callback=update_notify_callback)

    def update_position(self, vertex):
        xdata, ydata = vertex.coordinates

        if vertex == self.vertex1:
            self.vertex2.update_position(xdata + 2.4, ydata)
        else:
            self.vertex1.update_position(xdata - 2.4, ydata)

class ThresholdGate(AxesWidget):
    def __init__(self, verts, orientation='both', ax=None):
        self.orientation = orientation
        AxesWidget.__init__(self, ax)
        update_notify_callback = lambda vertex : self.update_position(vertex)
        self.vertex = Vertex(verts, ax, update_notify_callback=update_notify_callback)
        self.create_artist()

    def create_artist(self):
        vert = self.vertex.coordinates
        self.artist_list = []

        if self.orientation in ('both', 'horizontal'):
            self.hline = self.ax.axhline(y=vert[1], **STYLE.ActiveQuadGate)
            self.artist_list.append(self.hline)
        if self.orientation in ('both', 'vertical'):
            self.vline = self.ax.axvline(x=vert[0], **STYLE.ActiveQuadGate)
            self.artist_list.append(self.vline)

    def update_position(self, vertex):
        xdata, ydata = vertex.coordinates

        if hasattr(self, 'vline'):
            self.vline.set_xdata((xdata, xdata))
        if hasattr(self, 'hline'):
            self.hline.set_ydata((ydata, ydata))

class PolyDrawer(AxesWidget):
    """ Adapted from matplolib widget LassoSelector

    *ax* : :class:`~matplotlib.axes.Axes`
        The parent axes for the widget.
    *oncreated* : function
        Whenever the Polygon is created, the `oncreated` function is called and
        passed the PolyDrawer instance.
    """

    def __init__(self, ax, oncreated=None, lineprops=None):
        AxesWidget.__init__(self, ax)

        self.oncreated = oncreated
        self.verts = None

        if lineprops is None:
            lineprops = dict()
        self.line = Line2D([], [], **lineprops)
        self.line.set_visible(False)
        self.ax.add_line(self.line)

        self.connect_event('button_press_event', self.onpress)
        #self.connect_event('button_release_event', self.onrelease)
        self.connect_event('motion_notify_event', self.onmove)

    def ignore(self, event):
        #wrong_button = hasattr(event, 'button') and event.button != 1
        #return not self.active or wrong_button
        return event.inaxes != self.ax

    def onpress(self, event):
        if self.ignore(event): return

        if event.button == MOUSE.LEFT_CLICK:
            if self.verts is None:
                self.verts = [(event.xdata, event.ydata)]
                self.line.set_visible(True)
            else:
                self.verts.append((event.xdata, event.ydata))
            self.line.set_data(zip(*self.verts))
            self._update()
        elif event.button == MOUSE.RIGHT_CLICK:
            self.verts.append((event.xdata, event.ydata))
            self.line.set_data(zip(*self.verts))
            self._clean()
            self._update()

            if self.oncreated is not None:
                self.oncreated(self)

    def onmove(self, event):
        if self.ignore(event): return
        if self.verts is None: return

        x, y = zip(*self.verts)
        x = numpy.r_[x, event.xdata]
        y = numpy.r_[y, event.ydata]
        self.line.set_data(x, y)
        self._update()

    def _update(self):
        self.canvas.draw_idle()

    def _clean(self):
        self.disconnect_events()
        self.line.remove()

class Manager():
    gates = []

def create_vertex(event):
    #rect = DraggableRectangle.from_vert(plt.gca(), (event.xdata, event.ydata, 0.3, 0.3))
    rect = Vertex((event.xdata, event.ydata), plt.gca())
    Manager.gates.append(rect)
    Manager.cs.clear(event)
    Manager.cs.disconnect_events()
    del Manager.cs
    gcf().canvas.draw()

def create_threshold_gate(event):
    #rect = DraggableRectangle.from_vert(plt.gca(), (event.xdata, event.ydata, 0.3, 0.3))
    #rect = DoubleVertex((event.xdata, event.ydata), 'vertical', plt.gca())
    rect = DoubleVertex((event.xdata, event.ydata), plt.gca())
    Manager.gates.append(rect)
    Manager.th.clear(event)
    Manager.th.disconnect_events()
    del Manager.th
    gcf().canvas.draw()

def gate_drawer(event):
    """
    Launches different drawing tools
    """
    ax = plt.gca()
    if event.key in ['R', 'r']:
        print 'Launching rectangle selector'
        onselect.RS = RectangleSelector(ax, onselect, drawtype='box')
    elif event.key in ['T', 't']:
        print 'Launching circle creator'
        if not hasattr(Manager, 'th'):
            Manager.th = Cursor(ax)
            Manager.th.connect_event('button_press_event', create_threshold_gate)
    elif event.key in ['C', 'c']:
        print 'Launching circle creator'
        if not hasattr(Manager, 'cs'):
            Manager.cs = Cursor(ax)
            Manager.cs.connect_event('button_press_event', create_vertex)
    elif event.key.lower() in ['p']:
        print 'Launching circle creator'
        Manager.pd = PolyDrawer(ax, oncreated=create_polygon, lineprops = dict(color='k', marker='o'))
#Manager.rect = []

def create_polygon(poly_drawer_instance):
    verts = poly_drawer_instance.verts
    ax = poly_drawer_instance.ax
    pg = PolyGate(verts, ax)
    Manager.pg = pg
    del poly_drawer_instance
#
if __name__ == '__main__':
    fig = figure()
    ax = fig.add_subplot(111)
    xlim(-10, 10)
    ylim(-10, 10)
    #a = Vertex((0.3, 0.4), ax)
    connect('key_press_event', gate_drawer)
    #mn = LassoSelector(ax)
    show()
