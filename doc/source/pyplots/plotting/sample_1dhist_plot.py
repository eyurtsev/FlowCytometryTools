from FlowCytometryTools import FCMeasurement, ThresholdGate
import os, FlowCytometryTools
from pylab import *

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')

# datafile = '[insert path to your own fcs file]' 

# Load data
tsample = FCMeasurement(ID='Test Sample', datafile=datafile)
tsample = tsample.transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'], b=500.0)

# Plot
tsample.plot('Y2-A', bins=100, alpha=0.9, color='green');
grid(True)

# show() # <-- Uncomment when running as a script.
