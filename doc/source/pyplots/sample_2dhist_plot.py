from FlowCytometryTools import FCMeasurement, ThresholdGate
import os, FlowCytometryTools
from pylab import *

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')

# Load data
tsample = FCMeasurement(ID='Test Plate', datafile=datafile).transform('hlog', ('Y2-A', 'B1-A', 'V2-A'))

# Create gates
y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')

# Gate
gated_sample = tsample.gate(y2_gate)

# Plot
figure(figsize=(10, 5))
ax1 = subplot(121);
tsample.plot(['B1-A', 'Y2-A'], gates=[y2_gate], apply_gates=False, bins=100);
title('All Events');

ax2 = subplot(122, sharey=ax1, sharex=ax1);
gated_sample.plot(('B1-A', 'Y2-A'), bins=100);
title('Fluorescent Events');

tight_layout()
