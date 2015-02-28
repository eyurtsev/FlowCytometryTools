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

def transform_using_this_method(original_sample):
    """ This function implements a log transformation on the data. """
    # Copy the original sample
    new_sample = original_sample.copy()
    new_data = new_sample.data

    # Our transformation goes here
    new_data['Y2-A'] = log(new_data['Y2-A'])
    new_data = new_data.dropna() # Removes all NaN entries
    new_sample.data = new_data
    return new_sample

# Load data
sample = FCMeasurement(ID='Test Sample', datafile=datafile)

# Transform using our own custom method
custom_transform_sample = sample.apply(transform_using_this_method)

###
# To do this with a collection (a plate):
# compensated_plate = plate.apply(transform_using_this_method, 
#                   output_format='collection')

# Plot
custom_transform_sample.plot(['Y2-A'], color='green', alpha=0.9);
grid(True)

title('Custom log transformation')

#show() # <-- Uncomment when running as a script.
