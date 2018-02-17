from __future__ import print_function

import os

try:
    import wx
except ImportError:
    print('You are missing wx dependencies, so dialogs will not work.')
except Exception as e:
    print('Your wx python raised the following exception: {0}'.format(e))


# Our normal wxApp-derived class, as usual
def select_multi_directory_dialog():
    """ Opens a directory selection dialog
        Style - specifies style of dialog (read wx documentation for information)
    """
    import wx.lib.agw.multidirdialog as MDD

    app = wx.App(0)
    dlg = MDD.MultiDirDialog(None, title="Select directories", defaultPath=os.getcwd(),
                             agwStyle=MDD.DD_MULTIPLE | MDD.DD_DIR_MUST_EXIST)

    if dlg.ShowModal() != wx.ID_OK:
        dlg.Destroy()
        return

    paths = dlg.GetPaths()

    dlg.Destroy()
    app.MainLoop()

    return paths


def select_directory_dialog(windowTitle, defaultPath=os.getcwd(), style=None):
    """ Opens a directory selection dialog
        Style - specifies style of dialog (read wx documentation for information)
    """
    app = wx.App(None)

    if style == None:
        style = wx.DD_DIR_MUST_EXIST

    dialog = wx.DirDialog(None, windowTitle, defaultPath=defaultPath, style=style)

    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path


def open_file_dialog(windowTitle, wildcard, defaultDir=os.getcwd(), style=None, parent=None):
    """ Opens a wx widget file select dialog.
        Wild card specifies which kinds of files are allowed.
        Style - specifies style of dialog (read wx documentation for information)
    """

    if parent == None:
        app = wx.App(None)

    if style == None:
        style = wx.OPEN | wx.CHANGE_DIR

    dialog = wx.FileDialog(parent, windowTitle, defaultDir=defaultDir, wildcard=wildcard,
                           style=style)

    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path


def save_file_dialog(wildcard):
    """
        Show a save file dialog.
        TODO: This is not fully implemented.
    """
    app = wx.App(None)
    # style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Save file as ...', defaultDir=os.getcwd(), defaultFile="",
                           wildcard=wildcard, style=wx.SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
        print("You chose the following filename: %s" % path)
    else:
        path = None
    dialog.Destroy()
    return path


def select_option_dialog(windowTitle, optionList):
    """ Opens a select option dialog.
    Select the option by double clicking.
    TODO: Clean up this function
    TODO: Improve interface (i.e., add cancel, OK)
    """

    class OptionFrame(wx.Frame):
        selectedOption = None

        def __init__(self, windowTitle, optionList):
            wx.Frame.__init__(self, None, -1, windowTitle, size=(250, 200))
            panel = wx.Panel(self, -1)
            listBox = wx.ListBox(panel, -1, (20, 20), (80, 120), optionList, wx.LB_SINGLE)
            listBox.SetSelection(0)
            self.Bind(wx.EVT_LISTBOX_DCLICK, self.doubleclick)
            self.optionList = optionList

        def doubleclick(self, event):
            index = event.GetSelection()
            value = self.optionList[index]
            OptionFrame.selectedOption = (index, value)
            self.Close()

    app = wx.PySimpleApp()
    OptionFrame(windowTitle, optionList).Show()
    app.MainLoop()

    return OptionFrame.selectedOption

