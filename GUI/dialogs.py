import os
import wx
import wx.lib.agw.multidirdialog as MDD

def selectOption(message, channelList):
    """ # TODO Clean up this function """
    class option(): # Used For modifying by Reference in the OptionFrame class... Ugly.. What's a better solution :/
        pass

    class OptionFrame(wx.Frame):
        def __init__(self, message, channelList, mOption):
            wx.Frame.__init__(self, None, -1, message, size=(250, 200))
            panel = wx.Panel(self, -1)
            listBox = wx.ListBox(panel, -1, (20, 20), (80, 120), channelList, wx.LB_SINGLE)
            listBox.SetSelection(0)
            self.Bind(wx.EVT_LISTBOX_DCLICK, self.doubleclick)
            self.mOption = mOption

        def doubleclick(self,event):
            self.mOption.value = event.GetSelection()
            self.Close()

    app = wx.PySimpleApp()
    b = option()
    a = OptionFrame(message, channelList, b)
    a.Show()
    app.MainLoop()

    output = b.value

    return output


def openFile(message, wildcard):
    """ Opens a wx widget file select dialog.
    wild card specifies which kinds of files are allowed. """
    app = wx.App(None)
    style=wx.OPEN | wx.CHANGE_DIR
    dialog = wx.FileDialog(None, message, defaultDir=os.getcwd(), wildcard=wildcard, style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path

def saveFile(wildcard):
    """
    Create and show the Save FileDialog
    """
    app = wx.App(None)
    #style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Save file as ...', defaultDir=os.getcwd(), defaultFile="", wildcard=wildcard, style=wx.SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
        print "You chose the following filename: %s" % path
    else:
        path = None
    dialog.Destroy()
    return path

