from FlowCytometryTools import FCMeasurement, ThresholdGate
import os, FlowCytometryTools
from pylab import *

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')

# Load data
tsample = FCMeasurement(ID='Test Plate', datafile=datafile).transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'])

# Create gates
y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')

# Gate
high_rfp = tsample.gate(y2_gate)
low_rfp  = tsample.gate(~y2_gate)

# Plot
ax1 = subplot(1, 2, 1)
tsample.plot(['B1-A', 'Y2-A'], gates=[y2_gate], apply_gates=False, bins=300);

ax2 = subplot(1, 2, 2)
high_rfp.plot(['B1-A', 'Y2-A'], gates=[y2_gate], apply_gates=False, kind='scatter', alpha=0.5, color='r');
low_rfp.plot(['B1-A', 'Y2-A'], apply_gates=False, alpha=0.5, color='k', kind='scatter');

# Adjust font sizes
ax1.tick_params(axis='both', which='major', labelsize='x-small')
ax2.tick_params(axis='both', which='major', labelsize='x-small')

# show()
