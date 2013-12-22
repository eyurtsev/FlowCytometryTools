import matplotlib
from matplotlib.widgets import  RectangleSelector, Cursor, AxesWidget
from pylab import *
import pylab as pl
from numpy import random
import numpy
from FlowCytometryTools import FCMeasurement
from GoreUtilities.util import to_list


## TODO
# 1. Make it impossible to pick multiple vertexes at once. (right now if vertex are too close they will be selected.)
# 2. Make verties live in 1d and 2d (not just 2d). This will simplify
# some of the code for gates that use only 1d.

class MOUSE:
    LEFT_CLICK = 1
    RIGHT_CLICK = 3

class BaseVertex(object):
    def __init__(self, coordinates, update_notify_callback=None):
        """
        coordinates : dictionary
            keys : names of dimensions
            values : coordinates in each dimension
        """
        self.spawn_list = None
        self.coordinates = coordinates
        self.update_notify_callback = update_notify_callback

    def spawn(self, ax, spawn_channels):
        """
        'd1' can be shown on ('d1', 'd2') or ('d1')
        'd1', 'd2' can be shown only on ('d1', 'd2') or on ('d2', 'd1')

        This means that the channels on which the vertex
        is defined has to be a subset of the spawn_channels

        spawn_channels : names of channels on which to spawn
            the vertex
        """
        if len(spawn_channels) != len(set(spawn_channels)):
            raise Exception('Spawn channels must be unique')

        if not set(self.coordinates.keys()).issubset(set(spawn_channels)):
            raise Exception('Check that this is implemented correctly. Exception in the meantime.')

        if len(spawn_channels) == 1:
            verts = self.coordinates.get(spawn_channels[0], None), None
        else:
            verts = tuple([self.coordinates.get(ch, None) for ch in spawn_channels])

        def callback(svertex):
            ch = svertex.channels
            coordinates = svertex.coordinates
            new_coordinates = {k : v for k, v in zip(ch, coordinates)}
            self.update_coordinates(new_coordinates)

        spawned_vertex = SpawnableVertex(verts, ax, callback)
        spawned_vertex.channels = spawn_channels

        if self.spawn_list is None:
            self.spawn_list = []

        self.spawn_list.append(spawned_vertex)

        return spawned_vertex

    def update_coordinates(self, new_coordinates):
        """
        new_coordinates : dict
        """
        self.coordinates.update(new_coordinates)

        for svertex in self.spawn_list:
            verts = tuple([self.coordinates.get(ch, None) for ch in svertex.channels])

            if len(svertex.channels) == 1: # This means a histogram
                svertex.update_position(verts[0], None)
            else:
                svertex.update_position(verts[0], verts[1])

        if hasattr(self.update_notify_callback, '__call__'):
            self.update_notify_callback(self)


class SpawnableVertex(AxesWidget):
    """
    Defines a moveable vertex. The vertex must be associated
    wth an axis.

    The update_notify_callback function is called whenever the
    vertex is updated.

    coordinates - n 2-tuple

    ((1st dimension name, 1st dimension coordinate),
     (2nd dimension name, 2nd dimension coordinate),
     ...
     (nth dimension name, nth dimension coordinate))

    Actually only need this at the moment for 1 or 2 dimensions
    n dimensions are not needed.

    The idea is that a lower dimensional "vertex"
    can be visualized on a higher dimensional space

    For example,

    (d1, 0.1) would appear in (d1, d2) space as a straight line
    with d1=0.1
    """
    def __init__(self, coordinates, ax, update_notify_callback=None):
        AxesWidget.__init__(self, ax)
        self.update_notify_callback = update_notify_callback
        self.selected = False

        self.coordinates = tuple([c if c is not None else 0.5 for c in coordinates]) # Replaces all Nones with 0.5

        self.trackx = coordinates[0] is not None
        self.tracky = coordinates[1] is not None

        if not self.trackx and not self.tracky:
            raise Exception('Mode not supported')

        self.artist = None

        self.create_artist()
        self.connect_event('pick_event', lambda event : self.pick(event))
        self.connect_event('motion_notify_event', lambda event : self.motion_notify_event(event))
        #self.connect_event('button_press_event', lambda event : self.mouse_button_press(event))
        self.connect_event('button_release_event', lambda event : self.mouse_button_release(event))

    def create_artist(self):
        """
        decides whether the artist should be visible
        or not in the current axis

        current_axis : names of x, y axis
        """
        verts = self.coordinates

        if not self.tracky:
            trans = self.ax.get_xaxis_transform(which='grid')
        elif not self.trackx:
            trans = self.ax.get_yaxis_transform(which='grid')
        else:
            trans = self.ax.transData

        self.artist = pl.Line2D([verts[0]], [verts[1]], transform=trans, picker=10)
        self.update_looks('active')
        self.ax.add_artist(self.artist)

    def remove(self):
        """ Removes the vertex & disconnects events """
        if self.artist is not None:
            self.artist.remove()
        self.disconnect_events()

    def ignore(self, event):
        """ Ignores events. """
        if hasattr(event, 'inaxes'):
            if event.inaxes != self.ax:
                return True
        else:
            return False

    def pick(self, event):
        if self.artist != event.artist: return
        if self.ignore(event): return
        self.selected = not self.selected

    def mouse_button_release(self, event):
        if self.ignore(event): return
        if self.selected: self.selected = False

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
        self.canvas.draw()

    def update_looks(self, state):
        if state == 'active':
            style = {'color' : 'red', 'marker' : 's', 'ms' : 8}
        else:
            style = {'color' : 'black', 'marker' : 's', 'ms' : 5}
        self.artist.update(style)

    def set_visible(self, visible=True):
        for artist in to_list(self.artist):
            artist.set_visible(visible)

class BaseGate(object):
    """ Holds information regarding all the vertexes. """
    def __init__(self, coordinates_list, gate_type, update_notify=None):
        """
        verts is a list of tuples each tuple represents a vertex
        """
        self.coordinates = coordinates_list
        self.gate_type = gate_type
        self.verts = [BaseVertex(coordinates, self.vertex_update_callback) for coordinates in coordinates_list]
        self.update_notify = update_notify
        self.spawn_list = []

    def spawn(self, ax, spawn_channels):
        """ Spawns a graphical gate that can be used to update the coordinates of the current gate. """
        self.spawn_list.append(self.gate_type(self.verts, ax, spawn_channels))

    def vertex_update_callback(self, *args):
        for sgate in self.spawn_list:
            sgate.update_position()

    def get_generation_code(self, **gen_code_kwds):
        """
        Generates python code that can create the gate.
        """
        #if isinstance(self, PolyGate):
            #region = 'in'
            #vert_list = ['(' + ', '.join(map(lambda x : '{:.2f}'.format(x), vert)) + ')' for vert in self.vert]
        #else:
            #region = "?"
            #vert_list = ['{:.2f}'.format(vert) for vert in self.vert]
#
        #vert_list = '[' + ','.join(vert_list) + ']'
#
        #format_string = "{name} = {0}({1}, {2}, region='{region}', name='{name}')"
        #return format_string.format(self.__class__.__name__, vert_list,
                                #self.channels, name=self.name, region=region)

        gen_code_kwds.setdefault('name', self.name)
        gen_code_kwds.setdefault('region', self.region)
        gen_code_kwds.setdefault('gate_type', self.gate_type)
        gen_code_kwds.setdefault('verts', self.verts)

        if isinstance(self.channels, str):
            gen_code_kwds.setdefault('channels', "'{0}'".format(self.channels))
        else:
            gen_code_kwds.setdefault('channels', self.channels)

        format_string = "{name} = {gate_type}({verts}, {channels}, region='{region}', name='{name}')"
        return format_string.format(**gen_code_kwds)

class PlottableGate(object):
    def __init__(self, channels, vertex_list, toolbar, name):
        self.toolbar = toolbar
        self.name = name
        self.region = '?'
        self.gate_type = self.__class__.__name__
        self.channels = channels
        self._spawned_vertexes = [vert.spawn(self.ax, channels) for vert in vertex_list]
        self.create_artist()
        self.activate()

    def _update(self):
        self.canvas.draw()

    def delete(self):
        for artist in self.artist_list:
            artist.remove()
        for vertex in to_list(self.vertex):
            vertex.remove()
        self._update()

    def _change_activation(self, new_state):
        if not hasattr(self, 'state') or self.state != new_state:
            self.state = new_state
            for vertex in to_list(self.vertex):
                vertex.update_looks(self.state)
            self.update_looks()
            self._update()

    def activate(self): self._change_activation('active')
    def inactivate(self): self._change_activation('inactive')

    def set_visible(self, visible):
        for artist in self.artist_list:
            artist.set_visible(visible)
        for vertex in to_list(self.vertex):
            vertex.set_visible(visible)
        self._update()

    def set_visibility_based_on_axis(self, channels):
        """ Sets the visibility of the gate based
        on the currently viewed channels """
        print 'setting visibility'
        print 'cur channels', channels
        print 'self', self.channels
        visible = (channels == self.channels)
        self.set_visible(visible)

    @property
    def vertex(self):
        # TODO REFACTOR
        return self._spawned_vertexes

    @property
    def coordinates(self):
        return [vert.coordinates for vert in self._spawned_vertexes]

class PolyGate(AxesWidget, PlottableGate):
    def __init__(self, vertex_list, ax, spawn_channels, name=None):
        AxesWidget.__init__(self, ax)
        toolbar = None
        PlottableGate.__init__(self, spawn_channels, vertex_list, toolbar, name)

    def create_artist(self):
        self.poly = pl.Polygon(self.coordinates, color='k', fill=False)
        self.artist_list = to_list(self.poly)
        self.ax.add_artist(self.poly)

    def update_position(self):
        self.poly.set_xy(self.coordinates)
        self.toolbar.set_active_gate(self)

    def update_looks(self):
        """ Updates the looks of the gate depending on state. """
        if self.state == 'active':
            style = {'color' : 'red', 'linestyle' : 'solid', 'fill' : False}
        else:
            style = {'color' : 'black', 'fill' : False}
        self.poly.update(style)


class ThresholdGate(AxesWidget, PlottableGate):
    def __init__(self, verts, orientation, ax, toolbar, name):
        AxesWidget.__init__(self, ax)
        PlottableGate.__init__(self, toolbar, name)

        ## Set orientation and channels on which the gate is defined
        self.orientation = orientation

        if toolbar.current_channels is None:
            channel = None, None
        else:
            channel = toolbar.current_channels

        if orientation == 'vertical':
            self.channels = channel[0]
            self.gate_type = 'ThresholdGate'
        elif orientation == 'horizontal':
            self.channels = channel[1]
            self.gate_type = 'ThresholdGate'
        else:
            self.channels = tuple(channel)
            self.gate_type = 'QuadGate'

        trackx = orientation in ('both', 'vertical')
        tracky = orientation in ('both', 'horizontal')

        ## Set up call back events
        update_notify_callback = lambda vertex : self.update_position(vertex)

        self.vertex = SpawnableVertex(verts, ax, update_notify_callback=update_notify_callback,
                    trackx=trackx, tracky=tracky)
        self.create_artist()

    def create_artist(self):
        vert = self.vertex.coordinates
        self.artist_list = []
        if self.orientation in ('both', 'horizontal'):
            self.hline = self.ax.axhline(y=vert[1], color='k')
            self.artist_list.append(self.hline)
        if self.orientation in ('both', 'vertical'):
            self.vline = self.ax.axvline(x=vert[0], color='k')
            self.artist_list.append(self.vline)
        self.activate()

    def update_position(self, vertex):
        xdata, ydata = vertex.coordinates

        if hasattr(self, 'vline'):
            self.vline.set_xdata((xdata, xdata))
        if hasattr(self, 'hline'):
            self.hline.set_ydata((ydata, ydata))

        self.toolbar.set_active_gate(self)

    def update_looks(self):
        """ Updates the looks of the gate depending on state. """
        if self.state == 'active':
            style = {'color' : 'red', 'linewidth' : 2}
        else:
            style = {'color' : 'black', 'linewidth' : 1}

        for artist in self.artist_list:
            artist.update(style)

class PolyDrawer(AxesWidget):
    """
    Adapted from matplolib widget LassoSelector
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
        self.canvas.draw()

    def _clean(self):
        self.disconnect_events()
        self.line.remove()

class FCToolBar(object):
    """
    Manages gate creation widgets.
    """
    def __init__(self, ax):
        self.gates = []
        self.fig = ax.figure
        self.ax = ax
        self._plt_data = None
        self.active_gate = None
        self.sample = None
        self.canvas = self.fig.canvas
        self.key_handler_cid = self.canvas.mpl_connect('key_press_event', lambda event : key_press_handler(event, self.canvas, self))
        self.gate_num = 1
        self.current_channels = 'd1', 'd2'

    def disconnect_events(self):
        self.canvas.mpl_disconnect(self.key_handler_cid)

    def add_gate(self, gate):
        self.gates.append(gate)
        self.set_active_gate(gate)

    def delete_active_gate(self):
        if self.active_gate is not None:
            self.gates.remove(self.active_gate)
            self.active_gate.delete()
            self.active_gate = None

    def set_active_gate(self, gate):
        if self.active_gate is None:
            self.active_gate = gate
            gate.activate()
        elif self.active_gate is not gate:
            self.active_gate.inactivate()
            self.active_gate = gate
            gate.activate()

    def _get_next_gate_name(self):
        gate_name = 'gate{0}'.format(self.gate_num)
        self.gate_num +=1
        return gate_name

    def create_threshold_gate_widget(self, orientation):
        """
        Call this widget to create a threshold gate.
        Orientation : 'horizontal' | 'vertical' | 'both'
        """
        ax = self.ax
        fig = self.fig

        def clear_cursor(cs):
            cs.disconnect_events()
            cs.clear(None)
            del cs
            fig.canvas.draw()

        if hasattr(self, 'cs') and self.cs is not None:
            clear_cursor(self.cs)

        def create_threshold_gate(event, orientation, ax):
            gate = ThresholdGate((event.xdata, event.ydata),
                        orientation, ax, self,
                        self._get_next_gate_name())
            self.add_gate(gate)
            clear_cursor(self.cs)

        vertOn  = orientation in ['both', 'vertical']
        horizOn = orientation in ['both', 'horizontal']

        self.cs = Cursor(ax, vertOn=vertOn, horizOn=horizOn)
        self.cs.connect_event('button_press_event',
                lambda event : create_threshold_gate(event, orientation, ax))

    def create_polygon_gate_widget(self):
        """
        Call this function to start drawing a polygon on the ax.
        """
        def create_polygon(poly_drawer_instance):
            verts = poly_drawer_instance.verts
            gate = PolyGate(verts, self.ax, self,
                    self._get_next_gate_name())
            self.add_gate(gate)
            self.pd.disconnect_events()
            del poly_drawer_instance

        self.pd = PolyDrawer(self.ax, oncreated=create_polygon, lineprops = dict(color='k', marker='o'))

    ####################
    ### Loading Data ###
    ####################

    def load_fcs(self, filepath=None, parent=None):
        ax = self.ax

        if parent is None:
            parent = self.fig.canvas

        from GoreUtilities import dialogs

        if filepath is None:
            filepath = dialogs.open_file_dialog('Select an FCS file to load',
                        'FCS files (*.fcs)|*.fcs', parent=parent)

        if filepath is not None:
            self.sample = FCMeasurement('temp', datafile=filepath).transform('hlog')
            print 'WARNING: hlog transforming all data.'
            self._sample_loaded_event()
            self.plot_data()

    def load_measurement(self, measurement):
        self.sample = measurement.copy()
        self._sample_loaded_event()

    def _sample_loaded_event(self):
        if self.sample is not None:
            if self.current_channels == None:
                # Assigns first two channels by default if none have been specified yet.
                self.current_channels = list(self.sample.channel_names[0:2])

            self.set_axis(self.current_channels)
            self.plot_data()

    def set_axis(self, channels):
        """ Sets the x and y axis """
        channels = tuple([ch.encode("UTF-8") for ch in channels]) # To get rid of u's
        self.current_channels = channels
        for gate in self.gates:
            gate.set_visibility_based_on_axis(channels)
        self.plot_data()

    ####################
    ### Plotting Data ##
    ####################

    def plot_data(self):
        """ Plots the loaded data """
        if self.sample is None: return
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
            self.current_channels = sample.channel_names[:2]

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

    def get_generation_code(self):
        """
        Returns python code that generates all drawn gates.
        """
        code_list = [gate.get_generation_code() for gate in self.gates]
        code_list.sort()
        code_list = '\n'.join(code_list)
        return code_list

def key_press_handler(event, canvas, toolbar=None):
    """
    Handles keyboard shortcuts for the FCToolbar.
    """
    if event.key is None: return

    key = event.key.encode('ascii', 'ignore')

    if key in ['1']:
        toolbar.create_polygon_gate_widget()
    elif key in ['2', '3', '4']:
        orientation = {'2' : 'both', '3' : 'horizontal', '4' : 'vertical'}[key]
        toolbar.create_threshold_gate_widget(orientation)
    elif key in ['9']:
        toolbar.delete_active_gate()
    elif key in ['0']:
        toolbar.load_fcs()
    elif key in ['8']:
        for gate in toolbar.gates:
            gate.set_visible(False)
    elif key in ['7']:
        for gate in toolbar.gates:
            gate.set_visible(True)

class Globals():
    pass

if __name__ == '__main__':
    def example1():
        fig = figure()
        ax = fig.add_subplot(1, 4, 1)
        ax2 = fig.add_subplot(1, 4, 2)
        ax3 = fig.add_subplot(1, 4, 3)
        ax4 = fig.add_subplot(1, 4, 4)
        #xlim(-1, 1)
        #ylim(-1, 1)
        #manager = FCToolBar(ax)
        def x(*args):
            pass
        #verts = (('d1', 0.1))
        #verts = {'d1' : 0.8}
        verts = {'d1' : 0.8, 'd2' : 0.2}
        #verts = (0.1, 0.1)
        Globals.bv = BaseVertex(verts, x)
        Globals.bv.spawn(ax, ('d1', 'd2'))
        Globals.bv.spawn(ax2, ('d2', 'd1'))
        Globals.bv.spawn(ax3, ('d1', 'd2'))
        Globals.bv.spawn(ax4, ('d1', 'd2'))
        #manager.v = Vertex(verts, ax, x, True, True)
        #Globals.bv.update_coordinates({'d2' : 0.7, 'd1' : 0.9})
        show()
    def example2():
        fig = figure()
        ax = fig.add_subplot(1, 2, 1)
        ax2 = fig.add_subplot(1, 2, 2)
        #xlim(-1, 1)
        #ylim(-1, 1)
        #manager = FCToolBar(ax)
        def x(*args):
            pass
        #verts = (('d1', 0.1))
        #verts = {'d1' : 0.8}
        verts = ({'d1' : 0.8, 'd2' : 0.2},
                 {'d1' : 0.4, 'd2' : 0.4},
                 {'d1' : 0.7, 'd2' : 0.8})
        verts2 = ({'d1' : 0.9, 'd2' : 0.4},
                 {'d1' : 0.6, 'd2' : 0.2},
                 {'d1' : 0.8, 'd2' : 0.6})
        Globals.bv = BaseGate(verts, PolyGateRework, x)
        Globals.bv2 = BaseGate(verts2, PolyGateRework, x)
        Globals.bv.spawn(ax, ('d1', 'd2'))
        Globals.bv.spawn(ax2, ('d2', 'd1'))
        Globals.bv2.spawn(ax, ('d1', 'd2'))
        #Globals.bv.spawn(ax, ('d1', 'd2'))
        #Globals.bv.spawn(ax2, ('d2', 'd1'))
        #Globals.bv.spawn(ax3, ('d1', 'd2'))
        #Globals.bv.spawn(ax4, ('d1', 'd2'))
        #manager.v = Vertex(verts, ax, x, True, True)
        #Globals.bv.update_coordinates({'d2' : 0.7, 'd1' : 0.9})
        show()

    example2()
