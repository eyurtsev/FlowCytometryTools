#!/usr/bin/env python
import matplotlib.pylab as pl

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from matplotlib.figure import Figure

import wx
from gate_manager import GateManager

class FCWidget(FigureCanvas):
    def __init__(self, parent, ID):
        self.fig1 = Figure()
        self.ax1 = self.fig1.add_subplot(111)
        super(FigureCanvas, self).__init__(parent, ID, self.fig1)
        self.initialize_gate_manager()

    def initialize_gate_manager(self, fcs_filepath=None, channel_names=None, gate_path=None):
        """
        """
        ######################
        # Create window
        ######################
        self.gate_manager = GateManager(self.ax1, self.fig1)

        if fcs_filepath is not None:
            self.load_fcs(fcs_filepath)

        GateManager.current_channels = channel_names

        #def create_poly_gate(*args):
            #self.gate_manager.set_state(STATE_GK.START_DRAWING)

    def load_fcs(self, fcs_filepath=None):
        self.gate_manager.load_fcs(fcs_filepath)


if __name__ == '__main__':
    pass



################
# Garbage code
################

        #def list_gates(*args):
            #print('='*80)
            #print('Gates created\n' + 80*'-')
            #print('\n'.join([str(g) for g in GateManager.gateList]))
#
        #def load_fcs(*args):
            #gateKeeper.load_fcs()
#
#
        #def create_quad_gate(*args):
            #gateKeeper.set_state(STATE_GK.START_DRAWING_QUAD_GATE)
#
        #buttonList = [
                #{'Label' : 'Load FCS\nFile',                  'Button Location' : buttonSizes, 'event': load_fcs},
                ##{'Label' : 'Load Gates\nfrom File',           'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.load_gates('Choose a gates file', '*.xml')},
                ##{'Label' : 'Save Current\nGates to File',     'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.save_gates('Gate File (*.xml)|*.xml')},
                #{'Label' : 'List Gates',                      'Button Location' : buttonSizes, 'event': list_gates},
                #{'Label' : 'Polygon Gate',                    'Button Location' : buttonSizes, 'event': create_poly_gate},
                #{'Label' : 'Quad Gate',                       'Button Location' : buttonSizes, 'event': create_quad_gate},
                #{'Label' : 'Delete Gate',                     'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.set_state(STATE_GK.DELETE_GATE)},
                ##{'Label' : 'Quit',                            'Button Location' : buttonSizes, 'event': lambda do : pl.close()}]
                #]
#
        #for thisIndex, thisButton in enumerate(buttonList):
            #thisButton['Button Location'][0] = 0.05 + thisIndex * buttonSpacing
            #thisButton['Axes'] = pl.axes(thisButton['Button Location'])
            #thisButton['Reference'] = Button(thisButton['Axes'], thisButton['Label'])
            #thisButton['Reference'].on_clicked(thisButton['event'])

