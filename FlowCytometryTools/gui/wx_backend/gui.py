#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx

from FlowCytometryTools.gui import fc_widget
from FlowCytometryTools.gui.wx_backend.wireframe import GeneratedWireframe


class GUIEmbedded(GeneratedWireframe):
    def __init__(self, *args, **kwargs):
        GeneratedWireframe.__init__(self, *args, **kwargs)
        self.fig = self.canvas.figure
        self.ax = self.fig.add_subplot(111)
        self.fcgatemanager = fc_widget.FCGateManager(self.ax)
        self._update_available_channels()

    def load_measurement(self, measurement):
        self.fcgatemanager.load_measurement(measurement)
        self._update_available_channels()

    def load_fcs(self, filepath=None):
        self.fcgatemanager.load_fcs(filepath=filepath, parent=self)
        self._update_available_channels()

    def btnLoadFCS(self, event):
        self.load_fcs()

    def btnQuitApp(self, event):
        self.fcgatemanager.close()
        self.Close(1)

    def btn_choose_x_channel(self, event):
        self.update_widget_channels()

    def btn_choose_y_channel(self, event):
        self.update_widget_channels()

    def btn_create_poly_gate(self, event):
        self.fcgatemanager.create_gate_widget('poly')

    def btn_create_quad_gate(self, event):
        self.fcgatemanager.create_gate_widget('quad')

    def btn_create_horizontal_threshold_gate(self, event):
        self.fcgatemanager.create_gate_widget('horizontal threshold')

    def btn_create_vertical_threshold_gate(self, event):
        self.fcgatemanager.create_gate_widget('vertical threshold')

    def btn_delete_gate(self, event):
        self.fcgatemanager.remove_active_gate()

    def btn_gen_code(self, event):
        generated_code = self.fcgatemanager.get_generation_code()
        self.tb_gen_code.SetValue(generated_code)

    def _update_available_channels(self):
        if self.fcgatemanager.sample is not None:
            options = list(self.fcgatemanager.sample.channel_names)
        else:
            options = list(['d1', 'd2', 'd3'])  # For testing
        self.x_axis_list.Clear()
        self.x_axis_list.InsertItems(options, 0)
        self.y_axis_list.Clear()
        self.y_axis_list.InsertItems(options, 0)
        self.x_axis_list.Select(0)
        self.y_axis_list.Select(1)
        self.update_widget_channels()

    def update_widget_channels(self):
        """
        Parameters
        -------------
        axis : 'x' or 'y'
        event : pick of list text
        """
        sel1 = self.x_axis_list.GetSelection()
        sel2 = self.y_axis_list.GetSelection()

        if sel1 >= 0 and sel2 >= 0:
            channel_1 = self.x_axis_list.GetString(sel1)
            channel_2 = self.y_axis_list.GetString(sel2)
            self.fcgatemanager.set_axes((channel_1, channel_2), self.ax)


class GUILauncher(object):
    """ Use this to launch the wx-based fdlow cytometry app """

    def __init__(self, filepath=None, measurement=None):
        if filepath is not None and measurement is not None:
            raise ValueError('You can only specify either filepath or measurement, but not both.')

        self.app = wx.App(False)
        self.main = GUIEmbedded(None, -1, "")
        self.app.SetTopWindow(self.main)
        if filepath is not None:
            self.main.load_fcs(filepath)
        if measurement is not None:
            self.main.load_measurement(measurement)
        self.run()

    def run(self):
        self.main.Show()
        self.app.MainLoop()
