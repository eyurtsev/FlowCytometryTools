#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.5 on Sun Dec 29 21:35:52 2013
import wx

# begin wxGlade: extracode
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
# end wxGlade


class GeneratedWireframe(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GeneratedWireframe.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.x_axis_list = wx.ListBox(self, -1, choices=["Test1", "Test2", "Test3"], style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.sizer_3_staticbox = wx.StaticBox(self, -1, "x-axis")
        self.y_axis_list = wx.ListBox(self, -1, choices=["Test1", "Test2", "Test3"], style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.sizer_4_staticbox = wx.StaticBox(self, -1, "y-axis")
        self.button_load_fcs = wx.Button(self, -1, "Load FCS")
        self.button_horz_threshold_gate = wx.Button(self, -1, "---")
        self.button_vertical_threshold_gate = wx.Button(self, -1, "|")
        self.button_interval_gate = wx.Button(self, -1, "|--|")
        self.button_polygon_gate = wx.Button(self, -1, "Polygon Gate")
        self.button_quad_gate = wx.Button(self, -1, "Quad Gate")
        self.button_delete_gate = wx.Button(self, -1, "Delete Gate")
        self.button_quit = wx.Button(self, wx.ID_EXIT, "")
        self.button_controls_staticbox = wx.StaticBox(self, -1, "")
        self.canvas = FigureCanvas(self, -1, Figure())
        self.navtoolbar = NavigationToolbar(self.canvas)
        self.btn_generate_code = wx.Button(self, -1, "Generate Code")
        self.tb_gen_code = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.sizer_8_staticbox = wx.StaticBox(self, -1, "")
        self.tree_ctrl_1 = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS | wx.TR_NO_LINES | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)
        self.sizer_9_staticbox = wx.StaticBox(self, -1, "Gates")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LISTBOX, self.btn_choose_x_channel, self.x_axis_list)
        self.Bind(wx.EVT_LISTBOX, self.btn_choose_y_channel, self.y_axis_list)
        self.Bind(wx.EVT_BUTTON, self.btnLoadFCS, self.button_load_fcs)
        self.Bind(wx.EVT_BUTTON, self.btn_create_horizontal_threshold_gate, self.button_horz_threshold_gate)
        self.Bind(wx.EVT_BUTTON, self.btn_create_vertical_threshold_gate, self.button_vertical_threshold_gate)
        self.Bind(wx.EVT_BUTTON, self.btn_create_poly_gate, self.button_polygon_gate)
        self.Bind(wx.EVT_BUTTON, self.btn_create_quad_gate, self.button_quad_gate)
        self.Bind(wx.EVT_BUTTON, self.btn_delete_gate, self.button_delete_gate)
        self.Bind(wx.EVT_BUTTON, self.btnQuitApp, self.button_quit)
        self.Bind(wx.EVT_BUTTON, self.btn_gen_code, self.btn_generate_code)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: GeneratedWireframe.__set_properties
        self.SetTitle("Flow Cytometry")
        self.Hide()
        self.x_axis_list.SetSelection(0)
        self.y_axis_list.SetSelection(0)
        self.button_load_fcs.SetToolTip("Launches a file dialog to select an FCS file to load")
        self.button_interval_gate.Enable(False)
        self.tb_gen_code.SetMinSize((400, 100))
        self.tb_gen_code.SetToolTip("Automatically generates python code that can create the drawn gates")
        self.tree_ctrl_1.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: GeneratedWireframe.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1b = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_9_staticbox.Lower()
        sizer_9 = wx.StaticBoxSizer(self.sizer_9_staticbox, wx.HORIZONTAL)
        self.sizer_8_staticbox.Lower()
        sizer_8 = wx.StaticBoxSizer(self.sizer_8_staticbox, wx.HORIZONTAL)
        widget_sizer = wx.BoxSizer(wx.VERTICAL)
        self.button_controls_staticbox.Lower()
        button_controls = wx.StaticBoxSizer(self.button_controls_staticbox, wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_4_staticbox.Lower()
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        self.sizer_3_staticbox.Lower()
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        sizer_3.Add(self.x_axis_list, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_4.Add(self.y_axis_list, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_1b.Add(sizer_2, 0, wx.EXPAND, 0)
        button_controls.Add(self.button_load_fcs, 0, 0, 0)
        button_controls.Add(self.button_horz_threshold_gate, 0, 0, 0)
        button_controls.Add(self.button_vertical_threshold_gate, 0, 0, 0)
        button_controls.Add(self.button_interval_gate, 0, 0, 0)
        button_controls.Add(self.button_polygon_gate, 0, 0, 0)
        button_controls.Add(self.button_quad_gate, 0, 0, 0)
        button_controls.Add(self.button_delete_gate, 0, 0, 0)
        button_controls.Add(self.button_quit, 0, 0, 0)
        widget_sizer.Add(button_controls, 0, wx.EXPAND, 1)
        widget_sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND, 0)
        widget_sizer.Add(self.navtoolbar, 0, wx.EXPAND, 0)
        sizer_1b.Add(widget_sizer, 1, wx.EXPAND, 0)
        sizer_7.Add(self.btn_generate_code, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_8.Add(self.tb_gen_code, 1, wx.EXPAND, 0)
        sizer_7.Add(sizer_8, 1, wx.EXPAND, 0)
        sizer_9.Add(self.tree_ctrl_1, 1, wx.EXPAND, 0)
        sizer_7.Add(sizer_9, 1, wx.EXPAND, 0)
        sizer_1b.Add(sizer_7, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_1b, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def btn_choose_x_channel(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_choose_x_channel' not implemented!")
        event.Skip()

    def btn_choose_y_channel(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_choose_y_channel' not implemented!")
        event.Skip()

    def btnLoadFCS(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btnLoadFCS' not implemented!")
        event.Skip()

    def btn_create_horizontal_threshold_gate(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_create_horizontal_threshold_gate' not implemented!")
        event.Skip()

    def btn_create_vertical_threshold_gate(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_create_vertical_threshold_gate' not implemented!")
        event.Skip()

    def btn_create_poly_gate(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_create_poly_gate' not implemented!")
        event.Skip()

    def btn_create_quad_gate(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_create_quad_gate' not implemented!")
        event.Skip()

    def btn_delete_gate(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_delete_gate' not implemented!")
        event.Skip()

    def btnQuitApp(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btnQuitApp' not implemented!")
        event.Skip()

    def btn_gen_code(self, event):  # wxGlade: GeneratedWireframe.<event_handler>
        print("Event handler `btn_gen_code' not implemented!")
        event.Skip()

# end of class GeneratedWireframe
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    generated_wireframe = GeneratedWireframe(None, -1, "")
    app.SetTopWindow(generated_wireframe)
    generated_wireframe.Show()
    app.MainLoop()
