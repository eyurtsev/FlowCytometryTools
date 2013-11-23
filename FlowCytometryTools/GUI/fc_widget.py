#!/usr/bin/env python
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pylab as pl

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

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
