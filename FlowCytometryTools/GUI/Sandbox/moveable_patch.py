from matplotlib.widgets import  RectangleSelector, Cursor, AxesWidget
from pylab import *
import pylab as pl


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
    def __init__(self, verts, ax=None, update_notify_callback=None):
        AxesWidget.__init__(self, ax)
        self.update_notify_callback = update_notify_callback
        self.selected = False
        self.verts = verts
        self.create_artist()
        self.connect_event('pick_event', lambda event : self.pick(event))
        self.connect_event('motion_notify_event', lambda event : self.motion_notify_event(event))
        #self.connect_event('button_press_event', lambda event : self.mouse_button_press(event))
        self.connect_event('button_release_event', lambda event : self.mouse_button_release(event))

    def create_artist(self):
        self.artist = pl.Line2D([self.verts[0]], [self.verts[1]], picker=5, marker='s', color='r', ms=10)
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
            self.verts = (event.xdata, event.ydata)
            self.update_position(*self.verts)

    def update_position(self, xdata, ydata):
        self.artist.set_xdata([xdata])
        self.artist.set_ydata([ydata])
        self._update()

    def _update(self):
        if self.update_notify_callback is not None:
            self.update_notify_callback(self)
        pl.gcf().canvas.draw_idle()


class ThresholdGate(Vertex):
    def __init__(self, verts, orientation='both', ax=None):
        self.orientation = orientation
        Vertex.__init__(self, verts, ax)

    def create_artist(self):
        vert = self.verts
        self.artist = pl.Line2D([vert[0]], [vert[1]], picker=5, **STYLE.ActiveQuadGateCenter)
        self.ax.add_artist(self.artist)
        self.artist_list = [self.artist]

        if self.orientation in ('both', 'horizontal'):
            self.hline = self.ax.axhline(y=vert[1], **STYLE.ActiveQuadGate)
            self.artist_list.append(self.hline)
        if self.orientation in ('both', 'vertical'):
            self.vline = self.ax.axvline(x=vert[0], **STYLE.ActiveQuadGate)
            self.artist_list.append(self.vline)
        self._update()

    def update_position(self, xdata, ydata):
        if hasattr(self, 'vline'):
            self.vline.set_xdata((xdata, xdata))
        if hasattr(self, 'hline'):
            self.hline.set_ydata((ydata, ydata))
        self.artist.set_xdata([xdata])
        self.artist.set_ydata([ydata])
        self._update()

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
    rect = ThresholdGate((event.xdata, event.ydata), 'vertical', plt.gca())
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
#Manager.rect = []
#
if __name__ == '__main__':
    fig = figure()
    ax = fig.add_subplot(111)
    xlim(-10, 10)
    ylim(-10, 10)
    a = Vertex((0.3, 0.4), ax)
    connect('key_press_event', gate_drawer)
    show()
