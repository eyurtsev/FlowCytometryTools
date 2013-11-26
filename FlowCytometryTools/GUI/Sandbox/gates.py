from matplotlib.widgets import  RectangleSelector, Cursor
from pylab import *
import pylab as pl

def debugging_print(x):
    pass


def euclid_distance((x1, y1), (x2, y2)):
    return numpy.sqrt((x1-x2)**2 + (y1 - y2)**2)

class MOUSE:
    leftClick = 1
    rightClick = 3

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

class PlottableGate(object):
    """ For use with GUI """
    def __init__(self):
        """
        """
        # GUI Attributes
        self.fig = pl.gcf()
        self.ax = pl.gca()

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

    def get_generation_code(self):
        """
        Generates python code that can create the gate.
        """
        if isinstance(self, PolyGate):
            region = 'in'
            vert_list = ['(' + ', '.join(map(lambda x : '{:.2f}'.format(x), vert)) + ')' for vert in self.vert]
        else:
            region = "?"
            vert_list = ['{:.2f}'.format(vert) for vert in self.vert]

        vert_list = '[' + ','.join(vert_list) + ']'

        format_string = "{name} = {0}({1}, {2}, region='{region}', name='{name}')"
        return format_string.format(self.__class__.__name__, vert_list,
                                self.channels, name=self.name, region=region)


class QuadGate(PlottableGate):
    """ Defines a polygon gate. """
    def __init__(self, vert, channels, region):
        #base_gates.Gate.__init__(self, vert=vert, channels=channels, region=region, name=name)
        PlottableGate.__init__(self)
        self.vert = vert
        self.channels = channels
        self.region = region
        self.create_artist()
        self.set_state('Active')
        self.connect(['mouse press', 'mouse release', 'mouse motion'])

    #@call_wrapper
    def create_artist(self):
        vert = self.vert
        self.vline = self.ax.axvline(x=vert[0], **STYLE.ActiveQuadGate)
        self.hline = self.ax.axhline(y=vert[1], **STYLE.ActiveQuadGate)

        picker = lambda artist, event : self.gate_picker(artist, event)
        self.center = pl.Line2D([vert[0]], [vert[1]], picker=picker, **STYLE.ActiveQuadGateCenter)
        self.ax.add_artist(self.center)
        self.artist_list = [self.vline, self.hline, self.center]
        self.fig.canvas.draw()


    def gate_picker(self, artist, event):
        print artist.x
        print event
        return False, {}

    #@call_wrapper
    def on_press(self, event):
        print 'here'
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


class DraggableRectangle:
    def __init__(self, rect):
        self.rect = rect
        self.press = None

    @classmethod
    def from_vert(cls, ax, verts):
        rect = Rectangle(verts[:2], *verts[2:], facecolor="grey")
        self = DraggableRectangle(rect)
        ax.add_patch(rect)
        return self

    def connect(self):
        'connect to all the events we need'
        self.cidpress = plt.gcf().canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = plt.gcf().canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = plt.gcf().canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        if plt.gcf().canvas.widgetlock.locked(): return
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.rect.axes: return

        contains, attrd = self.rect.contains(event)
        if not contains: return
        print 'event contains', self.rect.xy
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if plt.gcf().canvas.widgetlock.locked(): return
        if self.press is None: return
        if event.inaxes != self.rect.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        #print 'x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f'%(x0, xpress, event.xdata, dx, x0+dx)
        self.rect.set_x(x0+dx)
        self.rect.set_y(y0+dy)
        plt.gcf().canvas.draw()

    def on_release(self, event):
        'on release we reset the press data'
        if plt.gcf().canvas.widgetlock.locked(): return
        self.press = None
        plt.gcf().canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        plt.gcf().canvas.mpl_disconnect(self.cidpress)
        plt.gcf().canvas.mpl_disconnect(self.cidrelease)
        plt.gcf().canvas.mpl_disconnect(self.cidmotion)

def onselect(eclick, erelease):
  'eclick and erelease are matplotlib events at press and release'
  print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
  print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
  print ' used button   : ', eclick.button

  onselect.RS.set_active(False)

class Manager():
    pass


def cursor_button_press(event):
    #rect = DraggableRectangle.from_vert(plt.gca(), (event.xdata, event.ydata, 0.3, 0.3))
    rect = QuadGate((event.xdata, event.ydata), (0, 1), 'inside')
    a.append(rect)

    Manager.cs.clear(event)
    Manager.cs.disconnect_events()
    del Manager.cs
    gcf().canvas.draw()


def gate_drawer(event):
    """
    Launches different drawing tools
    """
    ax = plt.gca()
    if event.key in ['R', 'r']:
        print 'Launching rectangle selector'
        onselect.RS = RectangleSelector(ax, onselect, drawtype='box')
    if event.key in ['C', 'c']:
        print 'Launching circle creator'
        if not hasattr(Manager, 'cs'):
            Manager.cs = Cursor(ax)
            Manager.cs.connect_event('button_press_event', cursor_button_press)

fig = figure()
ax = fig.add_subplot(111)
a = []
Manager.rect = []

connect('key_press_event', gate_drawer)
xlim(0, 10)
ylim(0, 10)
show()
