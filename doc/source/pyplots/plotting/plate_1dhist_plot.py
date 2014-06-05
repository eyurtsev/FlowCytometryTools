from FlowCytometryTools import FCPlate, ThresholdGate
import os, FlowCytometryTools
from pylab import *
import matplotlib.pyplot as plt

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')

# Load plate
plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name').transform('hlog', channels=['Y2-A', 'B1-A'])

# Drop empty cols / rows
plate = plate.dropna()

# Create gates
y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')

# Plot
plate.plot('Y2-A', bins=200, apply_gates=False, normed=True, color='gray', alpha=0.9);

# show()
