from FlowCytometryTools import FCPlate
import os, FlowCytometryTools
from pylab import *
import matplotlib.pyplot as plt

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate02')

# Load plate
plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name').transform('hlog', channels=['Y2-A', 'B1-A'])

# Drop empty cols / rows
plate = plate.dropna()

# Plot
plate.plot(['B1-A', 'Y2-A'], bins=200);

# show()
