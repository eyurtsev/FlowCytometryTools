from FlowCytometryTools import FCPlate
from GoreUtilities import plot_heat_map
import os, FlowCytometryTools
from pylab import *
import matplotlib.pyplot as plt

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')

# datadir = '[insert path to your own folder with fcs files.]'
# Make sure that the files follow the correct naming convention for the 'name' parser.
# Alternatively, change the parser (see tutorial online for further information).

# Load plate
plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name')
plate = plate.transform('hlog', channels=['Y2-A', 'B1-A'], b=500.0)

# Drop empty cols / rows
plate = plate.dropna()

# Create a threshold gates
from FlowCytometryTools import ThresholdGate
y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')

# Plot
plate = plate.gate(y2_gate)
plot_heat_map(plate.counts(), include_values=True, show_colorbar=True,
        cmap=cm.Oranges)
title('Heat map of fluorescent counts on plate')

#show() # <-- Uncomment when running as a script.
