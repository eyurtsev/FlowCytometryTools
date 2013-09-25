#!/usr/bin/env python
"""
Contains the gate manager which keeps track of the order of gates and allows
user to choose which gates to interact with.
"""
from gate import PolygonGate, QuadGate, PolygonDrawer
import util
from util import call_wrapper
from FlowCytometryTools import FCMeasurement
from manager_states import STATE_GK
from matplotlib.widgets import Cursor

def debugging_print(msg):
    return util.debugging_print(msg, True)

class GateManager():
    """ This will maintain a list of all the active gates. """
    def __init__(self, ax, fig, gateList=None, parent=None):
        if gateList is not None: GateManager.gateList = gateList
        else: GateManager.gateList = []
        self.current_channels = None
        self.sample = None
        self.fig =  fig
        self.ax = ax
        self.set_state(STATE_GK.WAITING)
        self.parent = parent
        self.connect()
        self.cursorWidget = None
        self._temp = None
        self._plt_data = None

    def connect(self):
        #self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_mouse_motion  = self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_motion)
        self.cid_mouse_press   = self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.cid_keyboard_press = self.fig.canvas.mpl_connect('key_press_event', self.on_keyboard_press)
        #self.cidpick    = self.fig.canvas.mpl_connect('pick_event', self.on_mouse_pick)

    def disconnect(self):
        'disconnect all the stored connection ids'
        ## TODO Define disconnect event properly
        self.fig.canvas.mpl_disconnect(self.cid_mouse_press)
        self.fig.canvas.mpl_disconnect(self.cid_mouse_motion)
        self.fig.canvas.mpl_disconnect(self.cid_keyboard_press)
        #self.fig.canvas.mpl_disconnect(self.cidrelease)
        #self.fig.canvas.mpl_disconnect(self.cidpick)

    def on_mouse_motion(self, event):
        """ Motion events. """
        debugging_print(('Gate Keeper state: ', self.state))
        if self.state == STATE_GK.START_DRAWING_QUAD_GATE:
            if self.cursorWidget == None:
                self.cursorWidget = Cursor(self.ax)

    #@call_wrapper
    def on_mouse_press(self, event):
        """ Button press events. """
        debugging_print(('Mouse Press. Gate Keeper state: ', self.state))
        if self.state == STATE_GK.WAITING:
            if self._temp is not None:
                del self._temp
                self._temp = None

            ## Choose gate
            if len(GateManager.gateList) > 0:
                gates_to_inactivate = [thisGate for thisGate in GateManager.gateList if thisGate.state == 'Active']
                activated_a_gate = False

                for thisGate in GateManager.gateList:
                    if thisGate.contains(event):
                        if thisGate.state == 'Inactive':
                            thisGate.activate()
                        self.bring_gate_to_top_layer(thisGate)
                        activated_a_gate = True

                        if thisGate in gates_to_inactivate:
                            gates_to_inactivate.remove(thisGate)
                        break

                for gate in gates_to_inactivate:
                    if (activated_a_gate and gate is not thisGate) or not activated_a_gate:
                        gate.inactivate()

        elif self.state == STATE_GK.START_DRAWING_POLY_GATE:
            debugging_print('Creating a polygon gate')
            self.inactivate_all_gates()
            gate = PolygonDrawer(channels=self.current_channels, gate_manager=self)
            gate.on_press(event) # re raise last event
            self._temp = gate
            self.set_state(STATE_GK.KEEP_DRAWING)

        elif self.state == STATE_GK.START_DRAWING_QUAD_GATE:
            self.inactivate_all_gates()
            quadGate = QuadGate(vert=(event.xdata, event.ydata),
                    channels=self.current_channels,
                    name='Quad Gate', gate_manager=self, region='top left')
            self.add_gate(quadGate)
            self.cursorWidget = None
            self.set_state(STATE_GK.WAITING)

    def on_keyboard_press(self, event):
        if event.key == 'c':
            self.set_state(STATE_GK.START_DRAWING_POLY_GATE)
        elif event.key == 'w':
            debugging_print(GateManager.gateList)

    def set_axis(self, channels):
        """
        Sets the x and y axis
        """
        channels = tuple([ch.encode("UTF-8") for ch in channels]) # To get rid of u's

        self.current_channels = channels
        self.plot_data()
        self.show_visible_gates()

    def show_visible_gates(self):
        #print 'Current channels :', self.current_channels
        for thisGate in GateManager.gateList:
            debugging_print(thisGate.channels)
            debugging_print(self.current_channels)

            #print 'Gate channels :', thisGate.channels
            if thisGate.channels == self.current_channels:
                #print 'setting gate visible'
                thisGate.set_visible(True)
            else:
                thisGate.set_visible(False)
        self.fig.canvas.draw()

    #@call_wrapper
    def inactivate_all_gates(self):
        for gate in GateManager.gateList:
            gate.inactivate()

    #@call_wrapper
    def add_gate(self, gate):
        """ Adds the current gate to the gate list. """
        GateManager.gateList.insert(0, gate)#append(gate)

    def bring_gate_to_top_layer(self, gate):
        GateManager.gateList.remove(gate)
        GateManager.gateList.insert(0, gate)

    def remove_gate(self, gate):
        GateManager.gateList.remove(gate)
        del gate

    def get_active_gate(self):
        for thisGate in GateManager.gateList:
            if thisGate.active:
                debugging_print('Active gate is: ')
                debugging_print(thisGate)
                return thisGate

    #@call_wrapper
    def set_state(self, state):
        """ TODO Remove the handling of deleting gates here. """
        if state == STATE_GK.DELETE_GATE:
            activeGate = self.get_active_gate()
            if activeGate:
                activeGate.remove_gate()
            state = STATE_GK.WAITING

        self.ax.set_title(state)
        self.fig.canvas.draw()
        self.state = state

    def plot_data(self):
        """ Plots the loaded data """
        sample = self.sample

        ax = self.ax

        if self._plt_data is not None:
            self._plt_data.remove()
            del self._plt_data
            self._plt_data = None

        channels = self.current_channels

        if channels[0] == channels[1]:
            self._plt_data = sample.plot(channels[0], transform=('hlog', 'hlog'), ax=ax)
            xlabel = self.current_channels[0]
            ylabel = 'Counts'
        else:
            self._plt_data = sample.plot(channels, transform=('hlog', 'hlog'), ax=ax)
            xlabel = self.current_channels[0]
            ylabel = self.current_channels[1]

        bbox = self._plt_data.get_datalim(self.ax.transData)
        p0 = bbox.get_points()[0]
        p1 = bbox.get_points()[1]

        self.ax.set_xlim(p0[0], p1[0])
        self.ax.set_ylim(p0[1], p1[1])

        self.fig.canvas.draw()

    def load_fcs(self, filepath=None, parent=None):
        """

        """
        if filepath is None:
            from GoreUtilities import dialogs
            filepath = dialogs.open_file_dialog('Select an FCS file to load', 'FCS files (*.fcs)|*.fcs', parent=parent)

        # This can still be None if the user cancels in the dialog.
        if filepath is not None:
            self.sample = FCMeasurement('temp', datafile=filepath)

            if self.current_channels == None:
                # Assigns first two channels by default if none have been specified yet.
                self.current_channels = list(self.sample.channel_names[0:2])

            self.set_axis(self.current_channels)
            self.plot_data()


