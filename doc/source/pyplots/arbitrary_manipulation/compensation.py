"""
Demonstrates how to implement a custom transformation of the data.
"""
from FlowCytometryTools import FCMeasurement, ThresholdGate
import os, FlowCytometryTools
from pylab import *

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')

# datafile = '[insert path to your own fcs file]' 

def custom_compensate(original_sample):
    # Copy the original sample
    new_sample = original_sample.copy()
    new_data = new_sample.data
    original_data = original_sample.data

    # Our transformation goes here
    new_data['Y2-A'] = original_data['Y2-A'] - 0.15 * original_data['FSC-A']
    new_data['FSC-A'] = original_data['FSC-A'] - 0.32 * original_data['Y2-A']
    new_data = new_data.dropna() # Removes all NaN entries
    new_sample.data = new_data
    return new_sample

# Load data
sample = FCMeasurement(ID='Test Sample', datafile=datafile)
sample = sample.transform('hlog')

compensated_sample = sample.apply(custom_compensate)

###
# To do this with a collection (a plate):
# compensated_plate = plate.apply(compensate, output_format='collection')
#

# Plot
sample.plot(['Y2-A', 'FSC-A'], kind='scatter', color='gray', alpha=0.6, label='Original');
compensated_sample.plot(['Y2-A', 'FSC-A'], kind='scatter', color='green', alpha=0.6, label='Compensated');

legend(loc='best')
grid(True)

#show() # <-- Uncomment when running as a script.
