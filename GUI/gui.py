#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
from wireframe import GeneratedWireframe
from manager_states import STATE_GK

class GUIEmbedded(GeneratedWireframe):

    def load_fcs(self, filepath=None):
        self.fc_widget_ref.gate_manager.load_fcs(filepath=filepath, parent=self)

        # Quick fix. Should actually fire events
        if self.fc_widget_ref.gate_manager.sample is not None:
            options = list(self.fc_widget_ref.gate_manager.sample.channel_names)
            options.sort() # May not be necessary
            self.x_axis_list.Clear()
            self.x_axis_list.InsertItems(options, 0)
            self.y_axis_list.Clear()
            self.y_axis_list.InsertItems(options, 0)

    def btnLoadFCS(self, event):
        self.load_fcs()

    def btnQuitApp(self, event):
        self.Close(1)

    def btn_choose_x_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            gate_manager = self.fc_widget_ref.gate_manager
            current_channels = gate_manager.current_channels
            gate_manager.set_axis((new_channel, current_channels[1]))

    def btn_choose_y_channel(self, event):
        if event.GetExtraLong(): # Quick hack
            new_channel = event.GetString()
            gate_manager = self.fc_widget_ref.gate_manager
            current_channels = gate_manager.current_channels
            gate_manager.set_axis((current_channels[0], new_channel))

    def btn_create_poly_gate(self, event):
        self.fc_widget_ref.gate_manager.set_state(STATE_GK.START_DRAWING_POLY_GATE)

    def btn_create_quad_gate(self, event):
        self.fc_widget_ref.gate_manager.set_state(STATE_GK.START_DRAWING_QUAD_GATE)

    def btn_create_quad_gate(self, event):
        generated_code = self.fc_widget_ref.gate_manager.get_generated_code()
        self.tb_gen_code.SetValue(generated_code)

class FC_GUI(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.sample_viewer = GUIEmbedded(None, -1, "")
        self.SetTopWindow(self.sample_viewer)
        self.sample_viewer.Show()
        return 1

    def load_fcs(self, filepath):
        self.sample_viewer.load_fcs(filepath)

def parse_input():
    """
    Examples of use:
        Opens up the specified FCS file with channels showing B1-A and Y2-A
        python flowGUI.py ../tests/data/Plate01/CFP_Well_A4.fcs -c B1-A Y2-A
    """
    import argparse
    epilog = parse_input.__doc__

    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(metavar="FILE", dest="filename", help='fcs file to open', nargs='?', default=None)

    parser.add_argument("-c", "--channel-names", dest="channel_names", nargs='+', help="channel names to plot on the x and y axis")

    return parser.parse_args()

if __name__ == "__main__":
    import glob
    files = glob.glob('./*.fcs')[0]
    print files
    app = FC_GUI()
    app.load_fcs(files)
    app.MainLoop()

