import FlowCytometryTools
from FlowCytometryTools import test_data_dir, test_data_file

datadir = test_data_dir
datafile = test_data_file


# Working with individual FCS files

from FlowCytometryTools import FCMeasurement
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

# Deprecated usage, fix this
from pylab import *

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

import os
print(os.path.basename(plate['A3'].datafile))

plate = plate.dropna()
print(plate)


# Plotting

figure()
plate.plot(['Y2-A'], bins=100)

figure()
plate.plot(['B1-A', 'Y2-A'], bins=100, wspace=0.2, hspace=0.2)


# Accessing single wells

figure()
print(plate['A3'])
plate['A3'].plot(['Y2-A'], bins=100)


# Counting using the counts method

total_counts = plate.counts()
print(total_counts)

y2_counts = plate.gate(y2_gate).counts()
print(y2_counts)

outside_of_y2_counts = plate.gate(~y2_gate).counts()
print(outside_of_y2_counts)


# Counting on our own

def count_events(well):
    data = well.get_data()
    count = data.shape[0]
    return count

print(count_events(plate['A3']))
print(plate['A3'].apply(count_events))

total_counts_using_our_function = plate.apply(count_events)
print(type(total_counts_using_our_function))
print(total_counts_using_our_function)

print(plate.gate(y2_gate).apply(count_events))


# Calculating median fluorescence

def calculate_median_rfp(well):
    data = well.get_data()
    return data['Y2-A'].median()

print(calculate_median_rfp(plate['A3']))
print(plate.apply(calculate_median_rfp))
print(plate.gate(y2_gate).apply(calculate_median_rfp))



# Wait for key press before exiting script
test = input()
