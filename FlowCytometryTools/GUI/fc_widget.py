import matplotlib
from matplotlib.widgets import  RectangleSelector, Cursor, AxesWidget
import pylab as pl
from numpy import random
import numpy
from FlowCytometryTools import FCMeasurement
from GoreUtilities.util import to_list
import itertools


## TODO
# 1. Make it impossible to pick multiple vertexes at once. (right now if vertex are too close they will be selected.)

class MOUSE:
    LEFT_CLICK = 1
    RIGHT_CLICK = 3

class Event(object):
    """
    An event class for passing messages between different GUI.
    """
    CHANGE = 1
    VERTEX_REMOVED = 2
    BASE_GATE_CHANGED = 3
    def __init__(self, event_type, event_info=None):
        self.type = event_type
        self.info = event_info if event_info is not None else {}
    def __str__(self):
        return '{} : {}'.format(self.type, self.info)

class EventGenerator(object):
    """
    A mixin class that allows objects to fire events and
    register callback functions.
    """
    def callback(self, event=None):
        if event is None:
            event = Event('NA', {'caller' : self})
        else:
            event.info.update({'caller' : self})

        if hasattr(self, 'callback_list'):
            for func in self.callback_list:
                func(event)

    def add_callback(self, func):
        """ Registers a call back function """
        if func is None: return
        func_list = to_list(func)

        if not hasattr(self, 'callback_list'):
            self.callback_list = func_list
        else:
            self.callback_list.extend(func_list)

def _check_spawnable(source_channels, target_channels):
    """ Checks whether gate is spawnable on the target channels. """
    if len(target_channels) != len(set(target_channels)):
        raise Exception('Spawn channels must be unique')
    return source_channels.issubset(set(target_channels)) # Only allow spawn if source channels are subset of target

class BaseVertex(EventGenerator):
    def __init__(self, coordinates, callback_list=None):
        """
        coordinates : dictionary
            keys : names of dimensions
            values : coordinates in each dimension
        """
        self.spawn_list = None
        self.coordinates = coordinates
        self.add_callback(callback_list)

    def spawn(self, ax, target_channels):
        """
        'd1' can be shown on ('d1', 'd2') or ('d1')
        'd1', 'd2' can be shown only on ('d1', 'd2') or on ('d2', 'd1')

        Parameters
        --------------
        This means that the channels on which the vertex
        is defined has to be a subset of the channels

        channels : names of channels on which to spawn
            the vertex

        Returns
        -------------
        spawnedvertex if successful otherwise None
        """
        source_channels = set(self.coordinates.keys())
        is_spawnable = _check_spawnable(source_channels, target_channels)

        if not is_spawnable:
            return None

        if len(target_channels) == 1:
            verts = self.coordinates.get(target_channels[0], None), None
        else:
            verts = tuple([self.coordinates.get(ch, None) for ch in target_channels])

        def _callback(event):
            if event.type == Event.CHANGE:
                svertex = event.info['caller']
                ch = svertex.channels
                coordinates = svertex.coordinates
                new_coordinates = {k : v for k, v in zip(ch, coordinates)}
                self.update_coordinates(new_coordinates)
            elif event.type == Event.VERTEX_REMOVED:
                svertex = event.info['caller']
                self.spawn_list.remove(svertex)
            else:
                raise ValueError('Unrecognized event {}'.format(event))

        spawned_vertex = SpawnableVertex(verts, ax, _callback)
        spawned_vertex.channels = target_channels

        if self.spawn_list is None:
            self.spawn_list = []
        self.spawn_list.append(spawned_vertex)
        return spawned_vertex

    def remove(self):
        for s in list(self.spawn_list): # IMPORTANT: Create a new list, because original list is modified by remove()
            s.remove()

    def update_coordinates(self, new_coordinates):
        """
        new_coordinates : dict
        """
        #self.coordinates.update(new_coordinates)
        for k, v in new_coordinates.items():
            if k in self.coordinates:
                self.coordinates[k] = v

        for svertex in self.spawn_list:
            verts = tuple([self.coordinates.get(ch, None) for ch in svertex.channels])

            if len(svertex.channels) == 1: # This means a histogram
                svertex.update_position(verts[0], None)
            else:
                svertex.update_position(verts[0], verts[1])
        self.callback(Event(Event.BASE_GATE_CHANGED))


class SpawnableVertex(AxesWidget, EventGenerator):
    """
    Defines a moveable vertex. The vertex must be associated
    wth an axis.

    The callback_list function is called whenever the
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
    def __init__(self, coordinates, ax, callback_list=None):
        AxesWidget.__init__(self, ax)
        self.add_callback(callback_list)
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

        self.artist = pl.Line2D([verts[0]], [verts[1]], transform=trans, picker=15)
        self.update_looks('inactive')
        self.ax.add_artist(self.artist)

    def remove(self):
        self.artist.remove()
        self.disconnect_events()
        self.callback(Event(Event.VERTEX_REMOVED))

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
            vevent = Event(Event.CHANGE)
            self.callback(vevent)
            self._update()

    def update_position(self, xdata, ydata):
        if self.trackx:
            self.coordinates = xdata, self.coordinates[1]
            self.artist.set_xdata([xdata])
        if self.tracky:
            self.coordinates = self.coordinates[0], ydata
            self.artist.set_ydata([ydata])

    def _update(self):
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

class BaseGate(EventGenerator):
    """ Holds information regarding all the vertexes. """
    def __init__(self, coordinates_list, gate_type, name=None, callback_list=None):
        """
        coordinates_list : list of dictionaries
            each dictionary has dimension names as keys and coordinates (floats) as values
        """
        self.verts = [BaseVertex(coordinates, self.vertex_update_callback) for coordinates in coordinates_list]
        self.gate_type = gate_type
        self.name = name
        self.region = '?'
        self.add_callback(callback_list)
        self.spawn_list = []

    def spawn(self, channels, ax):
        """ Spawns a graphical gate that can be used to update the coordinates of the current gate. """
        if _check_spawnable(self.source_channels, channels):
            sgate = self.gate_type(self.verts, ax, channels)
            self.spawn_list.append(sgate)
            return sgate
        else:
            return None

    def remove_spawned_gates(self, spawn_gate=None):
        """ Removes all spawned gates. """
        if spawn_gate is None:
            for sg in list(self.spawn_list):
                self.spawn_list.remove(sg)
                sg.remove()
        else:
            spawn_gate.remove()
            self.spawn_list.remove(spawn_gate)

    def remove(self):
        """ Removes all spawn and the base vertexes. """
        for v in self.verts:
            v.remove()
        self.remove_spawned_gates()

    def vertex_update_callback(self, *args):
        for sgate in self.spawn_list:
            sgate.update_position()
        gevent = Event(Event.CHANGE)
        self.callback(gevent)

    def _refresh_activation(self):
        [sgate._change_activation(self.state) for sgate in self.spawn_list]

    def activate(self):
        self.state = 'active'
        self._refresh_activation()

    def inactivate(self):
        self.state = 'inactive'
        self._refresh_activation()

    def get_generation_code(self, **gencode):
        """
        Generates python code that can create the gate.
        """
        channels, verts = self.coordinates
        num_channels = len(channels)
        channels = ', '.join(["'{}'".format(ch) for ch in channels])

        gencode.setdefault('name',      self.name)
        gencode.setdefault('region',    self.region)

        ## TODO REFACTOR. TEMP FIX for quadgate.
        gate_type_name = self.gate_type.__name__

        if gate_type_name == 'ThresholdGate' and num_channels == 2:
            gate_type_name = 'QuadGate'

        gencode.setdefault('gate_type', gate_type_name)
        gencode.setdefault('verts',     verts)
        gencode.setdefault('channels',  channels)
        format_string = "{name} = {gate_type}({verts}, ({channels}), region='{region}', name='{name}')"
        return format_string.format(**gencode)

    def set_axis(self, ch, ax):
        self.remove_spawned_gates()
        sgate = self.spawn(ch, ax)
        self._refresh_activation()

    @property
    def source_channels(self):
        """ Returns a set describing the source channels on which the gate is defined. """
        source_channels = [v.coordinates.keys() for v in self.verts]
        return set(itertools.chain(*source_channels))

    @property
    def coordinates(self):
        source_channels = list(self.source_channels)
        source_channels.sort()
        coordinates = [[v.coordinates.get(ch) for v in self.verts] for ch in source_channels]
        coordinates = zip(*coordinates)
        return source_channels, coordinates

class PlottableGate(AxesWidget):
    def __init__(self, vertex_list, ax, channels, name=None):
        AxesWidget.__init__(self, ax)
        self.channels = channels
        self.name = name
        self.region = '?'
        self.gate_type = self.__class__.__name__

        self._spawned_vertex_list = [vert.spawn(self.ax, channels) for vert in vertex_list]
        [svertex.add_callback(self.handle_vertex_event) for svertex in self._spawned_vertex_list]
        self.create_artist()
        self.activate()

    def handle_vertex_event(self, event):
        if event.type == Event.VERTEX_REMOVED:
            self._spawned_vertex_list.remove(event.info['caller'])

    def _update(self):
        self.canvas.draw()

    def remove(self):
        # IMPORTANT Do not remove spawned vertexes from the _list directly. Use 
        # svertex.remove() method it will automatically udpate the list using the vertex_handler
        for artist in self.artist_list:
            artist.remove()
        for svertex in list(self._spawned_vertex_list):
            svertex.remove()
        self._update()

    def _change_activation(self, new_state):
        if not hasattr(self, 'state') or self.state != new_state:
            self.state = new_state
            for svertex in list(self._spawned_vertex_list):
                svertex.update_looks(self.state)
            self.update_looks()
            self._update()

    def activate(self):
        self._change_activation('active')

    def inactivate(self):
        self._change_activation('inactive')

    @property
    def coordinates(self):
        return [vert.coordinates for vert in self._spawned_vertex_list]

    @property
    def vertex(self):
        return self._spawned_vertex_list

    #def set_visible(self, visible):
        #for artist in self.artist_list:
            #artist.set_visible(visible)
        #for vertex in to_list(self.vertex):
            #vertex.set_visible(visible)
        #self._update()

class PolyGate(PlottableGate):
    def create_artist(self):
        self.poly = pl.Polygon(self.coordinates, color='k', fill=False)
        self.artist_list = to_list(self.poly)
        self.ax.add_artist(self.poly)

    def update_position(self):
        self.poly.set_xy(self.coordinates)

    def update_looks(self):
        """ Updates the looks of the gate depending on state. """
        if self.state == 'active':
            style = {'color' : 'red', 'linestyle' : 'solid', 'fill' : False}
        else:
            style = {'color' : 'black', 'fill' : False}
        self.poly.update(style)

class ThresholdGate(PlottableGate):
    def create_artist(self):
        trackx, tracky = self.trackxy
        coord = self.coordinates[0]
        self.artist_list = []

        if tracky:
            self.hline = self.ax.axhline(y=coord[1], color='k')
            self.artist_list.append(self.hline)
        if trackx:
            self.vline = self.ax.axvline(x=coord[0], color='k')
            self.artist_list.append(self.vline)
        self.activate()

    def update_position(self):
        xdata, ydata = self.coordinates[0]
        if hasattr(self, 'vline'):
            self.vline.set_xdata(xdata)
        if hasattr(self, 'hline'):
            self.hline.set_ydata(ydata)

    def update_looks(self):
        """ Updates the looks of the gate depending on state. """
        if self.state == 'active':
            style = {'color' : 'red', 'linestyle' : 'solid'}
        else:
            style = {'color' : 'black'}
        for artist in self.artist_list:
            artist.update(style)

    @property
    def trackxy(self):
        trackx, tracky = self.vertex[0].trackx, self.vertex[0].tracky
        return trackx, tracky


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
        self.line = pl.Line2D([], [], **lineprops)
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
                self.oncreated(self.verts, self)

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

    def remove_active_gate(self):
        if self.active_gate is not None:
            self.gates.remove(self.active_gate)
            self.active_gate.remove()
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
        self.gate_num += 1
        return gate_name

    def _handle_gate_events(self, event):
        self.set_active_gate(event.info['caller'])

    def create_gate_widget(self, kind):
        def create_gate(*args):
            canceled = False # TODO allow drawing tool to cancel
            verts = args[0]
            ch = self.current_channels
            verts = [dict(zip(ch, v)) for v in verts]

            if kind == 'poly':
                gate_type = PolyGate
            elif 'threshold' in kind or 'quad' in kind:
                gate_type = ThresholdGate

            # FIXME: This is very specific implementation
            if 'vertical' in kind:
                verts = [{ch[0] : v[ch[0]]} for v in verts]
            elif 'horizontal' in kind:
                if len(ch) == 1:
                    canceled = True
                else:
                    verts = [{ch[1] : v[ch[1]]} for v in verts]

            if not canceled:
                gate = BaseGate(verts, gate_type, name=self._get_next_gate_name(), callback_list=self._handle_gate_events)
                gate.spawn(ch, self.ax)
                self.add_gate(gate)

            clean_drawing_tools(kind)

        def start_drawing(kind):
            if kind == 'poly':
                self._drawing_tool = PolyDrawer(self.ax, oncreated=create_gate, lineprops=dict(color='k', marker='o'))
            elif kind == 'quad':
                self._drawing_tool = Cursor(self.ax, vertOn=1, horizOn=1)
            elif kind == 'horizontal threshold':
                self._drawing_tool = Cursor(self.ax, vertOn=0, horizOn=1)
            elif kind == 'vertical threshold':
                self._drawing_tool = Cursor(self.ax, vertOn=1, horizOn=0)

            if isinstance(self._drawing_tool, Cursor):
                self._drawing_tool.connect_event('button_press_event', lambda event : create_gate([(event.xdata, event.ydata)]))

        def clean_drawing_tools(kind):
            self._drawing_tool.disconnect_events()
            self._drawing_tool = None
            self.canvas.draw()

        start_drawing(kind)

    ####################
    ### Loading Data ###
    ####################

    def load_fcs(self, filepath=None, parent=None):
        ax = self.ax

        if parent is None:
            parent = self.fig.canvas

        if filepath is None:
            from GoreUtilities import dialogs
            filepath = dialogs.open_file_dialog('Select an FCS file to load',
                        'FCS files (*.fcs)|*.fcs', parent=parent)

        if filepath is not None:
            self.sample = FCMeasurement('temp', datafile=filepath)
            print 'WARNING: Data is raw (not transformation).'
            self._sample_loaded_event()

    def load_measurement(self, measurement):
        self.sample = measurement.copy()
        self._sample_loaded_event()

    def _sample_loaded_event(self):
        if self.sample is not None:
            self.current_channels = list(self.sample.channel_names[0:2])
            self.set_axis(self.current_channels, self.ax)
            self.plot_data()

    def set_axis(self, channels, ax):
        """
        channels : iterable of string
            each value corresponds to a channel names
            names must be unique
        """
        self.current_channels = channels

        for gate in self.gates:
            gate.set_axis(channels, ax)
        self.plot_data()

    def close(self):
        for gate in self.gates:
            gate.remove()
        self.disconnect_events()

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

        if len(channels) == 1: # Then histogram
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
        toolbar.create_gate_widget(kind='poly')
    elif key in ['2', '3', '4']:
        kind = {'2' : 'quad', '3' : 'horizontal threshold', '4' : 'vertical threshold'}[key]
        toolbar.create_gate_widget(kind=kind)
    elif key in ['9']:
        toolbar.remove_active_gate()
    elif key in ['0']:
        toolbar.load_fcs()
    elif key in ['a']:
        toolbar.set_axis(('d1', 'd2'), pl.gca())
    elif key in ['b']:
        toolbar.set_axis(('d2', 'd1'), pl.gca())
    elif key in ['c']:
        toolbar.set_axis(('d1', 'd3'), pl.gca())
    elif key in ['8']:
        print toolbar.get_generation_code()

class Globals():
    """ Used for testing only """
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
        Globals.bv.spawn(('d1', 'd2'), ax )
        Globals.bv.spawn(('d2', 'd1'), ax2)
        Globals.bv.spawn(('d1', 'd2'), ax3)
        Globals.bv.spawn(('d1', 'd2'), ax4)
        #manager.v = Vertex(verts, ax, x, True, True)
        #Globals.bv.update_coordinates({'d2' : 0.7, 'd1' : 0.9})
        show()
    def example2():
        fig = figure()
        ax = fig.add_subplot(1, 1, 1)
        #ax2 = fig.add_subplot(1, 2, 2)
        #xlim(-1, 1)
        #ylim(-1, 1)
        manager = FCToolBar(ax)
        def x(*args):
            print "This gate might not behave properly."
        #verts = (('d1', 0.1))
        #verts = ({'d1' : 0.8}, )#, 'd1' : 0.3}, )
        verts = ({'d2' : 0.8, 'd1' : 0.3}, )
        #verts = ({'d1' : 0.8, 'd2' : 0.2},
                 #{'d1' : 0.4, 'd2' : 0.4},
                 #{'d1' : 0.7, 'd2' : 0.8})
        #verts2 = ({'d1' : 0.9, 'd2' : 0.4},
                 #{'d1' : 0.6, 'd2' : 0.2},
                 #{'d1' : 0.8, 'd2' : 0.6})
        #gate = BaseGate(verts, PolyGate, 'gate1', x)
        #gate = BaseGate(verts, ThresholdGate, 'gate1', x)
        #manager.add_gate(gate)
        #Globals.bv2 = BaseGate(verts2, PolyGate, x)
        #gate.spawn(('d1', 'd2'), ax)
        #Globals.bv.remove_spawn()
        #Globals.bv2.spawn(ax, ('d1', 'd2'))
        #Globals.bv.spawn(ax, ('d1', 'd2'))
        #Globals.bv.spawn(ax2, ('d2', 'd1'))
        #Globals.bv.spawn(ax3, ('d1', 'd2'))
        #Globals.bv.spawn(ax4, ('d1', 'd2'))
        #manager.v = Vertex(verts, ax, x, True, True)
        #Globals.bv.update_coordinates({'d2' : 0.7, 'd1' : 0.9})
        show()
    def example3():
        fig = pl.figure()
        ax = fig.add_subplot(1, 1, 1)
        manager = FCToolBar(ax)
        pl.show()

    example3()
