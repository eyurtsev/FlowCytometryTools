from FlowCytometryTools import FCPlate
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

# Plot
plate.plot('Y2-A', bins=200, normed=True, color='gray', alpha=0.9, wspace=0.1, hspace=0.1);

# show() # <-- Uncomment when running as a script.
