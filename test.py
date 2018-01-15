import FlowCytometryTools
from FlowCytometryTools import test_data_dir, test_data_file
from FlowCytometryTools import FCMeasurement
import matplotlib.pyplot as plt
import numpy as np

# Deprecated usage, fix this
from pylab import *

datadir = test_data_dir
datafile = test_data_file


# Working with individual FCS files

sample = FCMeasurement(ID='Test Sample', datafile=datafile)


# Channel information

print(sample.channel_names)

print(sample.channels)


# Full metadata

print(type(sample.meta))

print(sample.meta.keys())

print(sample.meta['$SRC'])


# Accessing raw data

print(type(sample.data))

print(sample.data[['Y2-A', 'FSC-A']][:10])

print(type(sample.data.values))

print(sample.data[['Y2-A', 'FSC-A']][:10].values)

data = sample.data

print(data['Y2-A'].describe())

print(data.shape[0])

print(data['Y2-A'].median())


# Transformations

tsample = sample.transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'], b=500.0)


# Plotting 1D histograms

figure()
tsample.plot(['Y2-A'], bins=100)

figure()
grid(True)
tsample.plot(['Y2-A'], color='green', alpha=0.7, bins=100)


# Plotting 2D histograms

figure()
tsample.plot(['B1-A', 'Y2-A'])

figure()
tsample.plot(['B1-A', 'Y2-A'], cmap=cm.Oranges, colorbar=False)


# Plotting 2D scatter plots

figure()
tsample.plot(['B1-A', 'Y2-A'], kind='scatter', color='red', s=1, alpha=0.3)


# Gating

from FlowCytometryTools import ThresholdGate, PolyGate


# Creating gates programmatically

y2_gate = ThresholdGate(1000.0, ['Y2-A'], region='above')
b1_gate = ThresholdGate(2000.0, ['B1-A'], region='above')


# Plotting gates

figure()
tsample.plot(['Y2-A'], gates=[y2_gate], bins=100)
title('Gate Plotted')


# Applying gates

gated_sample = tsample.gate(y2_gate)
print(gated_sample.get_data().shape[0])

# The gated_sample is also an instance of FCMeasurement
figure()
gated_sample.plot(['Y2-A'], color='y', bins=100)
title('Gated sample')

#Let's compare the gated and ungated side by side
figure()
subplots_adjust(hspace=0.4)
ax1 = subplot(211)
tsample.plot(['Y2-A'], color='gray', bins=100, gates=[y2_gate])
title('Original Sample')
ax2 = subplot(212, sharey=ax1, sharex=ax1)
gated_sample.plot(['Y2-A'], color='y', bins=100, gates=[y2_gate])
title('Gated Sample')


# A better way to load data

from FlowCytometryTools import FCPlate
print(datadir)
plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name')
plate = plate.transform('hlog', channels=['Y2-A', 'B1-A'])
print(plate)








# Wait for key press before exiting script
test = input()
