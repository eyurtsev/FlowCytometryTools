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

# Create a threshold gates
y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')

# Gate
gated_sample = tsample.gate(y2_gate)

# Plot
ax1 = subplot(121);
tsample.plot('Y2-A', gates=[y2_gate], bins=100, alpha=0.9);
y2_gate.plot(color='k', linewidth=4, linestyle='-')
title('Original Sample');

ax2 = subplot(122, sharey=ax1, sharex=ax1);
gated_sample.plot('Y2-A', gates=[y2_gate], bins=100, color='y', alpha=0.9);
title('Gated Sample');

tight_layout()

#show() # <-- Uncomment when running as a script.
