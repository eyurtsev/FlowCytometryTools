#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import matplotlib
matplotlib.use('wxagg')
from wireframe import GeneratedWireframe
from manager_states import STATE_GK
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
import gate_toolbar

class GUIEmbedded(GeneratedWireframe):

    def __init__(self, *args, **kwargs):
        GeneratedWireframe.__init__(self, *args, **kwargs)
        self.fig = self.canvas.figure
        self.ax = self.fig.add_subplot(111)
        self.fc_toolbar = gate_toolbar.FCToolBar(self.ax)

    def _update_axes(self):
        if self.fc_toolbar.sample is not None:
            options = list(self.fc_toolbar.sample.channel_names)
            options.sort() # May not be necessary
            self.x_axis_list.Clear()
            self.x_axis_list.InsertItems(options, 0)
            self.y_axis_list.Clear()
            self.y_axis_list.InsertItems(options, 0)

    def add_toolbar(self):
        """
        See http://matplotlib.org/examples/user_interfaces/embedding_in_wx2.html
        for details
        """
        return
        self.canvas = self.fc_widget_ref.fig1.canvas
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
            # having a toolbar in a sizer. This work-around gets the buttons
            # back, but at the expense of having the toolbar at the top
            self.SetToolBar(self.toolbar)
        else:
            # On Windows platform, default window size is incorrect, so set
            # toolbar width to figure width.
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # As noted above, doesn't work for Mac.
            self.toolbar.SetSize(wx.Size(fw, th))
        # update the axes menu on the toolbar
        self.toolbar.update()
        return self.toolbar

    #def load_fc_measurement(self, measurement):
        #self.fc_widget_ref.gate_manager.load_measurement(measurement)
        #self._update_axes()

    def load_fcs(self, filepath=None):
        self.fc_toolbar.load_fcs(filepath=filepath, parent=self)
        self._update_axes()

    def btnLoadFCS(self, event):
        self.load_fcs()

    def btnQuitApp(self, event):
        print 'Application Exiting'
        for gate in self.fc_toolbar.gates:
            gate.disconnect_events()
        self.fc_toolbar.disconnect_events()
        self.Close(1)

    def btn_choose_x_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            current_channels = self.fc_toolbar.current_channels
            self.fc_toolbar.set_axis((new_channel, current_channels[1]))

    def btn_choose_y_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            new_channel = event.GetString()
            current_channels = self.fc_toolbar.current_channels
            self.fc_toolbar.set_axis((current_channels[0], new_channel))

    def btn_create_poly_gate(self, event):
        self.fc_toolbar.create_polygon_gate_widget()

    def btn_create_quad_gate(self, event):
        self.fc_toolbar.create_threshold_gate_widget('both')

    def btn_gen_code(self, event):
        generated_code = self.fc_toolbar.get_generation_code()
        self.tb_gen_code.SetValue(generated_code)


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    generated_wireframe = GUIEmbedded(None, -1, "")
    app.SetTopWindow(generated_wireframe)
    generated_wireframe.Show()
    app.MainLoop()

#class FC_GUI(wx.App):
    #def OnInit(self):
        #wx.InitAllImageHandlers()
        #self.sample_viewer = GUIEmbedded(None, -1, "")
        #self.SetTopWindow(self.sample_viewer)
        #self.sample_viewer.Show()
        #return 1
#
    #def load_fcs(self, filepath):
        #self.sample_viewer.load_fcs(filepath)
#
    #def load_fc_measurement(self, measurement):
        #self.sample_viewer.load_fc_measurement(measurement)
#
#def parse_input():
    #"""
    #OLD DO NOT USE
    #Examples of use:
        #Opens up the specified FCS file with channels showing B1-A and Y2-A
        #python flowGUI.py ../tests/data/Plate01/CFP_Well_A4.fcs -c B1-A Y2-A
    #"""
    #import argparse
    #epilog = parse_input.__doc__
    #parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    #parser.add_argument(metavar="FILE", dest="filename", help='fcs file to open', nargs='?', default=None)
    #parser.add_argument("-c", "--channel-names", dest="channel_names", nargs='+', help="channel names to plot on the x and y axis")
    #return parser.parse_args()

#def launch_from_fc_measurement(measurement):
    #"""
    #Launches the GUI from an FCmeasurement.
    #"""
    #app = FC_GUI()
    #app.load_fc_measurement(measurement)
    #app.MainLoop()


#if __name__ == "__main2__":
    #import glob
    #import os
    #import FlowCytometryTools
    #datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01', '*.fcs')
    #files = glob.glob(datadir)[0]
#
    ##files = glob.glob('./*.fcs')[0]
    ##files = glob.glob('datadir/')[0]
    #print files
    #app = FC_GUI()
    ##app.load_fcs(files)
    #app.MainLoop()
