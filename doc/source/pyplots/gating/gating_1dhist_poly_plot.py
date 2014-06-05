from FlowCytometryTools import FCMeasurement
import os, FlowCytometryTools
from pylab import *

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')

# datafile = '[insert path to your own fcs file]' 

# Load data
tsample = FCMeasurement(ID='Test Sample', datafile=datafile)
tsample = tsample.transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'], b=500.0)

# Create poly gate
from FlowCytometryTools import PolyGate

# HINT: If you have wx-python installed, then you can use the GUI to create the gate.
# You can launch the GUI by executing the command tsample.view_interactively()

gate1 = PolyGate([(-5.441e+02, 7.978e+03), (-8.605e+02, 6.739e+03), (-5.811e+02, 4.633e+03),
    (1.502e+03, 5.118e+03), (8.037e+02, 8.215e+03), (8.037e+02, 8.215e+03)], ('B1-A', 'Y2-A'), region='in', name='poly gate')

# Gate

gated_sample = tsample.gate(gate1)
inverted_sample = tsample.gate(~gate1) # Everything outside of gate1

# Plot
gated_sample.plot(('Y2-A', 'B1-A'), gates=[gate1], kind='scatter', color='red', alpha=0.9);
inverted_sample.plot(('Y2-A', 'B1-A'), kind='scatter', color='gray', alpha=0.9);

#show() # <-- Uncomment when running as a script.
