#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import matplotlib
matplotlib.use('wxagg')
from wireframe import GeneratedWireframe
import gate_toolbar

class GUIEmbedded(GeneratedWireframe):
    def __init__(self, *args, **kwargs):
        GeneratedWireframe.__init__(self, *args, **kwargs)
        self.fig = self.canvas.figure
        self.ax = self.fig.add_subplot(111)
        self.fc_toolbar = gate_toolbar.FCToolBar(self.ax)
        self._update_axes()

    def load_fc_measurement(self, measurement):
        self.fc_toolbar.load_measurement(measurement)
        self._update_axes()

    def load_fcs(self, filepath=None):
        self.fc_toolbar.load_fcs(filepath=filepath, parent=self)
        self._update_axes()

    def btnLoadFCS(self, event):
        self.load_fcs()

    def btnQuitApp(self, event):
        self.fc_toolbar.close()
        self.Close(1)

    def btn_choose_x_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            current_channels = self.fc_toolbar.current_channels
            self.fc_toolbar.set_axis((new_channel, current_channels[1]), self.ax)

    def btn_choose_y_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            current_channels = self.fc_toolbar.current_channels
            self.fc_toolbar.set_axis((current_channels[0], new_channel), self.ax)

    def btn_create_poly_gate(self, event):
        self.fc_toolbar.create_gate_widget('poly')

    def btn_create_quad_gate(self, event):
        self.fc_toolbar.create_gate_widget('quad')

    def btn_create_horizontal_threshold_gate(self, event):
        self.fc_toolbar.create_gate_widget('horizontal threshold')

    def btn_create_vertical_threshold_gate(self, event):
        self.fc_toolbar.create_gate_widget('vertical threshold')

    def btn_delete_gate(self, event):
        self.fc_toolbar.remove_active_gate()

    def btn_gen_code(self, event):
        generated_code = self.fc_toolbar.get_generation_code()
        self.tb_gen_code.SetValue(generated_code)

    def _update_axes(self):
        if self.fc_toolbar.sample is not None:
            options = list(self.fc_toolbar.sample.channel_names)
        else:
            options = list(['d1', 'd2', 'd3']) # Just a seed
        self.x_axis_list.Clear()
        self.x_axis_list.InsertItems(options, 0)
        self.y_axis_list.Clear()
        self.y_axis_list.InsertItems(options, 0)
        self.fc_toolbar.current_channels = options[0], options[1]

class FCGUI(object):
    """ Use this to launch the wx-based fdlow cytometry app """
    def __init__(self, filepath=None):
        self.app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        self.main = GUIEmbedded(None, -1, "")
        self.app.SetTopWindow(self.main)
        if filepath is not None:
            self.main.load_fcs(filepath)
        self.run()

    def run(self):
        self.main.Show()
        self.app.MainLoop()

if __name__ == "__main__":
    app = FCGUI('../tests/data/FlowCytometers/FACSCaliburHTS/Sample_Well_A02.fcs')
