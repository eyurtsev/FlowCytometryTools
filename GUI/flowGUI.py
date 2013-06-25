#!/usr/bin/env python
import numpy
import matplotlib.pylab as pl
from matplotlib.widgets import Button
import glob
from gate import GateKeeper, STATE_GK

#### KNOWN BUGS
### 1. I have an extra vertix somewhere [ should be fixed had to do with moving vertices first / last vertix separately. (strange matplotlib behavior)
### 2. It's too slow: coloring too many of the points
### 3. create gate -> delete gate -> create gate and cannot move vertix
### 4. after changing the axis (calling the wx widgets dialog) if the mouse hovers over the matplotlib toolbar (at the bottom) the program crashes.

def launchGUI(fcs_filepath=None, channel_names=None, gate_path=None):
    '''
        launches the GUI
    '''

    ######################
    # Create window
    ######################

    fig = pl.figure()
    fig.canvas.set_window_title('FCS GUI')
    ax = fig.add_axes([0.15, 0.30, 0.7, 0.60])
    #ax = fig.add_subplot(111)
    gateKeeper = GateKeeper(ax, fig)

    ######################
    ### Create Buttons ###
    ######################

    buttonSpacing = 0.15
    buttonSizes = [0.05, 0.05, buttonSpacing-0.03, 0.15]


    def list_gates(*args):
        print('='*80)
        print('Gates created\n' + 80*'-')
        print('\n'.join([str(g) for g in GateKeeper.gateList]))

    def load_fcs(*args):
        gateKeeper.load_fcs()

    def create_poly_gate(*args):
        gateKeeper.set_state(STATE_GK.START_DRAWING)

    def create_quad_gate(*args):
        gateKeeper.set_state(STATE_GK.START_DRAWING_QUAD_GATE)

    buttonList = [
            {'Label' : 'Load FCS\nFile',                  'Button Location' : buttonSizes, 'event': load_fcs},
            #{'Label' : 'Load Gates\nfrom File',           'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.load_gates('Choose a gates file', '*.xml')},
            #{'Label' : 'Save Current\nGates to File',     'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.save_gates('Gate File (*.xml)|*.xml')},
            {'Label' : 'List Gates',                      'Button Location' : buttonSizes, 'event': list_gates},
            {'Label' : 'Polygon Gate',                    'Button Location' : buttonSizes, 'event': create_poly_gate},
            {'Label' : 'Quad Gate',                       'Button Location' : buttonSizes, 'event': create_quad_gate},
            {'Label' : 'Delete Gate',                     'Button Location' : buttonSizes, 'event': lambda do : gateKeeper.set_state(STATE_GK.DELETE_GATE)},
            #{'Label' : 'Quit',                            'Button Location' : buttonSizes, 'event': lambda do : pl.close()}]
            ]

    for thisIndex, thisButton in enumerate(buttonList):
        thisButton['Button Location'][0] = 0.05 + thisIndex * buttonSpacing
        thisButton['Axes'] = pl.axes(thisButton['Button Location'])
        thisButton['Reference'] = Button(thisButton['Axes'], thisButton['Label'])
        thisButton['Reference'].on_clicked(thisButton['event'])

    GateKeeper.current_channels = channel_names

    pl.sca(ax)

    if fcs_filepath is not None:
        gateKeeper.load_fcs(fcs_filepath)

    pl.show()

    if len(GateKeeper.gateList) is not 0:
        return GateKeeper.gateList

def parseInput():
    """
    Examples of use:
        Opens up the specified FCS file with channels showing B1-A and Y2-A
        python flowGUI.py ../tests/data/EY_2013-05-03_EID_214_PID_1120_Piperacillin_Well_B7.001.fcs -c B1-A Y2-A
    """
    import argparse
    epilog = parseInput.__doc__

    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(metavar="FILE", dest="filename", help='fcs file to open', default=None)

    parser.add_argument("-c", "--channel-names", dest="channel_names", nargs='+', help="channel names to plot on the x and y axis")

    return parser.parse_args()



if __name__ == '__main__':
    pArgs = parseInput()
    launchGUI(pArgs.filename, pArgs.channel_names)
