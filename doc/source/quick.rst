.. _quick:

.. currentmodule:: FlowCytometryTools


.. ipython:: python
   :suppress:

   import numpy as np
   from numpy import shape, log, where, nan
   np.set_printoptions(precision=4, suppress=True)


******************
Quick Introduction
******************

Loading an FCS file
--------------------

First, we need to find our FCS files.

.. ipython:: python
	from FlowCytometryTools import FCPlate
	
	# You can insert your own directory instead of datadir here.
	import os, FlowCytometryTools # This import is only needed to locate the FlowCytometryTools directory 
	datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
	

.. ipython:: python
	print 'Loading files from directory path: {0}'.format(datadir)
    datafile = os.path.join(datadir, 'CFP_Well_A4.fcs')
    print 'Loading file from path: {0}'.format(datafile)
    sample = FCMeasurement(ID='Test Plate', datafile=datafile)

Transformations
--------------------------


Plotting
--------------------------

Gating
--------------------------

Working with plates
-------------------------

First, we will load all fcs files in a folder into a plate.

.. ipython:: python

	# Load the files
	plate = FCPlate.from_dir(ID='Test Plate', path=datadir)

Once a plate has been loaded, it's layout can be viewed by printing the plate object.

.. ipython:: python
	
	print plate

This plate contains many empty rows and columns, which may be dropped for convenience:

.. ipython:: python
	
	plate = plate.dropna()
	print plate
 
Next, we'll apply the hyperlog transform to the FSC-A and Y2-A channels of the entire plate:

.. ipython:: python
	
	hplate = plate.transform('hlog', channels=('FSC-A', 'Y2-A'))

The entire plate can be plotted:

.. ipython:: python
	
	@savefig quick_hlog_plate.png width=4.5in
	out = hplate.plot(('FSC-A', 'Y2-A'))	


Example 01: Counting the total number of events
------------------------------------------------


Example 02: Calculating the standard deviation of data that passes a given gate
---------------------------------------------------------------------------------


