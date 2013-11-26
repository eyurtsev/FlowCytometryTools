import matplotlib
matplotlib.use('wxagg')
from matplotlib.widgets import  RectangleSelector, Cursor, AxesWidget
from pylab import *
import pylab as pl
from numpy import random
import numpy
from FlowCytometryTools import FCMeasurement


class MOUSE:
    LEFT_CLICK = 1
    RIGHT_CLICK = 3

class Vertex(AxesWidget):
    """
    TODO Finish trackx, tracky to include mixed coordinate system.
    """
    def __init__(self, coordinates, ax=None, update_notify_callback=None,
                            trackx=True, tracky=True):
        AxesWidget.__init__(self, ax)
        self.update_notify_callback = update_notify_callback
        self.selected = False
        self.trackx = trackx
        self.tracky = tracky
        self.coordinates = coordinates
        self.create_artist()
        self.connect_event('pick_event', lambda event : self.pick(event))
        self.connect_event('motion_notify_event', lambda event : self.motion_notify_event(event))
        #self.connect_event('button_press_event', lambda event : self.mouse_button_press(event))
        self.connect_event('button_release_event', lambda event : self.mouse_button_release(event))

    def create_artist(self):
        verts = self.coordinates
        self.artist = pl.Line2D([verts[0]], [verts[1]], picker=10,
                                        marker='s', color='r', ms=10)
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
        if self.trackx:
            self.coordinates = xdata, self.coordinates[1]
            self.artist.set_xdata([xdata])
        if self.tracky:
            self.coordinates = self.coordinates[0], ydata
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

class ThresholdGate(AxesWidget):
    def __init__(self, verts, orientation='both', ax=None):
        self.orientation = orientation
        AxesWidget.__init__(self, ax)
        update_notify_callback = lambda vertex : self.update_position(vertex)

        trackx = orientation in ['both', 'vertical']
        tracky = orientation in ['both', 'horizontal']

        self.vertex = Vertex(verts, ax, update_notify_callback=update_notify_callback,
                    trackx=trackx, tracky=tracky)
        self.create_artist()

    def create_artist(self):
        vert = self.vertex.coordinates
        self.artist_list = []

        if self.orientation in ('both', 'horizontal'):
            self.hline = self.ax.axhline(y=vert[1])
            self.artist_list.append(self.hline)
        if self.orientation in ('both', 'vertical'):
            self.vline = self.ax.axvline(x=vert[0])
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

class FCToolBar():
    """
    Manages gate creation widgets.
    """
    def __init__(self):
        self.gates = []
        fig = figure()

        self.fig = fig
        self.ax = fig.add_subplot(111)
        self._plt_data = None
        self.current_channels = None

        xlim(-10, 10)
        ylim(-10, 10)
        connect('key_press_event', lambda event : self.gate_drawer(event, self.ax))
        show()

    def create_vertex(self, event):
        ax = self.ax
        vertex = Vertex((event.xdata, event.ydata), ax)
        self.gates.append(vertex)
        self.cs.disconnect_events()
        self.cs.clear(event)
        del self.cs
        self.fig.canvas.draw()

    def create_polygon(self, poly_drawer_instance):
        ax = self.ax
        verts = poly_drawer_instance.verts
        pg = PolyGate(verts, ax)
        self.pg = pg
        del poly_drawer_instance

    def create_threshold_gate(self, event, orientation, ax):
        gate = ThresholdGate((event.xdata, event.ydata), orientation, ax=ax)
        self.gates.append(gate)
        self.cs.clear(event)
        self.cs.disconnect_events()
        del self.cs
        gcf().canvas.draw()

    def load_fcs(self, parent=None):
        ax = self.ax

        if parent is None:
            parent = self.fig.canvas

        from GoreUtilities import dialogs
        filepath = dialogs.open_file_dialog('Select an FCS file to load',
                    'FCS files (*.fcs)|*.fcs', parent=parent)

        if filepath is not None:
            self.sample = FCMeasurement('temp', datafile=filepath).transform('hlog')
            #self._sample_loaded_event()

    def gate_drawer(self, event, ax):
        """
        Launches different drawing tools
        """
        if event.key.lower() in ['1']:
            self.pd = PolyDrawer(ax, oncreated=self.create_polygon, lineprops = dict(color='k', marker='o'))
        elif event.key in ['2', '3', '4']:
            orientation = {'2' : 'both', '3' : 'horizontal', '4' : 'vertical'}[event.key]

            if not hasattr(self, 'cs'):
                vertOn  = event.key in ['2', '4']
                horizOn = event.key in ['2', '3']
                self.cs = Cursor(ax, vertOn=vertOn, horizOn=horizOn)
                self.cs.connect_event('button_press_event',
                        lambda event : self.create_threshold_gate(event, orientation, ax))
        elif event.key in ['9', '9']:
            if not hasattr(self, 'cs'):
                self.cs = Cursor(ax)
                self.cs.connect_event('button_press_event', self.create_vertex)
        elif event.key in ['0']:
            self.load_fcs()
            self.plot_data()
        #if event.key in ['R', 'r']:
            #print 'Launching rectangle selector'
            #onselect.RS = RectangleSelector(ax, onselect, drawtype='box')

    def plot_data(self):
        """ Plots the loaded data """
        sample = self.sample
        ax = self.ax

        if self._plt_data is not None:
            if isinstance(self._plt_data, tuple):
                # This is the case for histograms which return a tuple
                patches = self._plt_data[2]
                map(lambda x : x.remove(), patches)
            else:
                self._plt_data.remove()
            del self._plt_data
            self._plt_data = None


        if self.current_channels is None:
            self.current_channels = sample.channel_names[4:6]

        channels = self.current_channels

        if channels[0] == channels[1]:
            self._plt_data = sample.plot(channels[0], ax=ax)
            xlabel = self.current_channels[0]
            ylabel = 'Counts'
        else:
            self._plt_data = sample.plot(channels, ax=ax)
            xlabel = self.current_channels[0]
            ylabel = self.current_channels[1]

        if hasattr(self._plt_data, 'get_datalim'):
            bbox = self._plt_data.get_datalim(self.ax.transData)
            p0 = bbox.get_points()[0]
            p1 = bbox.get_points()[1]

            self.ax.set_xlim(p0[0], p1[0])
            self.ax.set_ylim(p0[1], p1[1])
        else:
            # Then it's a histogram?
            xlims = self._plt_data[1]
            xlims = (xlims[0], xlims[-1])
            self.ax.set_xlim(xlims)
            self.ax.set_ylim(0, max(self._plt_data[0]))

        self.fig.canvas.draw()



class Global:
    pass

if __name__ == '__main__':
    Global.manager = FCToolBar()

###############################
def key_press_handler(event, canvas, toolbar=None):
    """
    Implement the default mpl key bindings for the canvas and toolbar
    described at :ref:`key-event-handling`

    *event*
      a :class:`KeyEvent` instance
    *canvas*
      a :class:`FigureCanvasBase` instance
    *toolbar*
      a :class:`NavigationToolbar2` instance

    """
    # these bindings happen whether you are over an axes or not

    if event.key is None:
        return

    # Load key-mappings from your matplotlibrc file.
    fullscreen_keys = rcParams['keymap.fullscreen']
    home_keys = rcParams['keymap.home']
    back_keys = rcParams['keymap.back']
    forward_keys = rcParams['keymap.forward']
    pan_keys = rcParams['keymap.pan']
    zoom_keys = rcParams['keymap.zoom']
    save_keys = rcParams['keymap.save']
    quit_keys = rcParams['keymap.quit']
    grid_keys = rcParams['keymap.grid']
    toggle_yscale_keys = rcParams['keymap.yscale']
    toggle_xscale_keys = rcParams['keymap.xscale']
    all = rcParams['keymap.all_axes']

    # toggle fullscreen mode (default key 'f')
    if event.key in fullscreen_keys:
        canvas.manager.full_screen_toggle()

    # quit the figure (defaut key 'ctrl+w')
    if event.key in quit_keys:
        Gcf.destroy_fig(canvas.figure)

    if toolbar is not None:
        # home or reset mnemonic  (default key 'h', 'home' and 'r')
        if event.key in home_keys:
            toolbar.home()
        # forward / backward keys to enable left handed quick navigation
        # (default key for backward: 'left', 'backspace' and 'c')
        elif event.key in back_keys:
            toolbar.back()
        # (default key for forward: 'right' and 'v')
        elif event.key in forward_keys:
            toolbar.forward()
        # pan mnemonic (default key 'p')
        elif event.key in pan_keys:
            toolbar.pan()
        # zoom mnemonic (default key 'o')
        elif event.key in zoom_keys:
            toolbar.zoom()
        # saving current figure (default key 's')
        elif event.key in save_keys:
            toolbar.save_figure()

    if event.inaxes is None:
        return

    # these bindings require the mouse to be over an axes to trigger

    # switching on/off a grid in current axes (default key 'g')
    if event.key in grid_keys:
        event.inaxes.grid()
        canvas.draw()
    # toggle scaling of y-axes between 'log and 'linear' (default key 'l')
    elif event.key in toggle_yscale_keys:
        ax = event.inaxes
        scale = ax.get_yscale()
        if scale == 'log':
            ax.set_yscale('linear')
            ax.figure.canvas.draw()
        elif scale == 'linear':
            ax.set_yscale('log')
            ax.figure.canvas.draw()
    # toggle scaling of x-axes between 'log and 'linear' (default key 'k')
    elif event.key in toggle_xscale_keys:
        ax = event.inaxes
        scalex = ax.get_xscale()
        if scalex == 'log':
            ax.set_xscale('linear')
            ax.figure.canvas.draw()
        elif scalex == 'linear':
            ax.set_xscale('log')
            ax.figure.canvas.draw()

    elif (event.key.isdigit() and event.key != '0') or event.key in all:
        # keys in list 'all' enables all axes (default key 'a'),
        # otherwise if key is a number only enable this particular axes
        # if it was the axes, where the event was raised
        if not (event.key in all):
            n = int(event.key) - 1
        for i, a in enumerate(canvas.figure.get_axes()):
            # consider axes, in which the event was raised
            # FIXME: Why only this axes?
            if event.x is not None and event.y is not None \
                    and a.in_axes(event):
                if event.key in all:
                    a.set_navigate(True)
                else:
                    a.set_navigate(i == n)

