.. _quick:

.. currentmodule:: FlowCytometryTools


.. ipython:: python
    :suppress:

    import numpy as np
    from numpy import shape, log, where, nan
    from pylab import figure, cm, title

    np.set_printoptions(precision=4, suppress=True)

    import os, FlowCytometryTools # This import is only needed to locate the FlowCytometryTools directory
    datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01')
    print 'Loading files from directory path: {0}'.format(datadir)

    datafile = os.path.join(datadir, 'RFP_Well_A3.fcs')
    print 'Loading file from path: {0}'.format(datafile)


******************
Quick Introduction
******************

Loading a single FCS file
--------------------------

To get cracking, we'll need some flow cytometry data (i.e., .fcs files).

We'll use the sample fcs files included with the package.

.. ipython:: python

	from FlowCytometryTools import FCMeasurement
    sample = FCMeasurement(ID='Test Plate', datafile=datafile)

.. note::
    
    To analyze your own data, set ``datafile`` to the of your .fcs file.
    (e.g., ``datafile=r'C:\data\my_very_awesome_data.fcs'``)

.. Windows users::
    Windows paths use a backslash (``\``) instead of a forward slash (``/``).

    The backslash character is a special character in many programming languages. 
    In order for python to interpret the backslash correctly, you must
    include the letter ``r`` before the path specification as was done above.

Want to know which channels were measured? No problem.

.. ipython:: python

    print sample.channel_names

.. hint::

    Usually, there's loads of useful information inside FCS files.

    Try the following:

    * ``sample.channels``
    * ``sample.meta``

    To interpret the meaning of some the fields, just google the specification for the FCS format.

Transformations
--------------------------

If you'd like to see your data (and make sense of it), you'll need to transform it. 

Let's apply an 'hlog' transformation to the ``Y2-A``, ``B1-A`` and ``V2-A`` channels, 
and save the transformed sample in ``tsample``.

.. ipython:: python

    tsample = sample.transform('hlog', ('Y2-A', 'B1-A', 'V2-A'))

.. note::
    You can read more about transformations here:
        TODO

Plotting
--------------------------

1d histograms
++++++++++++++++++++++++++

Let's start with 1d histograms.

.. ipython:: python

    figure();
	@savefig 1d_plot.png width=4.5in
    tsample.plot('B1-A', bins=100);


The plot function accepts all the same arguments as does the matplotlib histogram function.

.. ipython:: python

    figure();
	@savefig 1d_plot_B.png width=4.5in
    tsample.plot('B1-A', bins=100, alpha=0.7, color='green', normed=1);


2d histograms
++++++++++++++++++++++++++

If you feed the plot function with the names of two channels, you'll get a 2d histogram.

.. ipython:: python

    figure();
	@savefig 2d_plot_A.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A']);

The plot function accepts all the same arguments as does the matplotlib histogram function.

.. ipython:: python

    figure();
	@savefig 2d_plot_B.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A'], cmap=cm.Oranges, colorbar=False);

2d scatter plots
++++++++++++++++++++++

You can also plot scatter plots by providing the argument ``kind='scatter`` to the plot command.

Now, the plot function will behave like the matplotlib scatter function.

.. ipython:: python

    figure();
	@savefig 2d_scatter_plot_A.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A'], kind='scatter', color='red', s=1, alpha=0.3);

Gating
--------------------------

Load the gates we need from the library.

.. ipython:: python

    from FlowCytometryTools import ThresholdGate, PolyGate

Creating Gates
+++++++++++++++++++++++

When creating a gate, you will need to provide set(s) of coordinates, name(s) of channel(s) and the region. 
For example, the command below will set a gate that will pass only events where the Y2-A value is ABOVE the value 1000.0.

Let's create two gates. One gate will look for YFP positive events and the other
for CFP positive events.

.. ipython:: python

    y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')
    b1_gate = ThresholdGate(2000.0, 'B1-A', region='above')

GUI for creating gates 
++++++++++++++++++++++++

(alpha release) (NOT YET IMPLEMENTED. SKIP SECTION)

You can launch the GUI for creating the gates, by calling the view() method of a selected well.

Plotting Gates
+++++++++++++++++

.. ipython:: python

    title('Sample with gates drawn but not applied')
    tsample.plot(['B1-A', 'Y2-A'], gates=[y2_gate], apply_gates=False);

.. ipython:: python

    title('Sample with gates drawn and applied')
    tsample.plot(['B1-A', 'Y2-A'], gates=[y2_gate], apply_gates=True);

Calculations
---------------------

Working with plates
---------------------

If you're doing high-throughput measurements on the flow cytometer, you will hardly
ever want to load single fcs files. Instead, you'll want to be working with plates.

Loading Data
++++++++++++++++++

First, we will load all fcs files in a folder into a plate.

.. ipython:: python

	from FlowCytometryTools import FCPlate
    plate = FCPlate.from_dir(ID='Demo Plate', path=datadir).transform('hlog', channels=('Y2-A', 'B1-A'))

.. note::

    The line above is equivalent to the two steps below:
        (1) plate = FCPlate.from_dir(ID='Demo Plate', path=datadir)
        (2) plate = plate.transform('hlog', channels=('Y2-A', 'B1-A'))                                                                 

Once a plate has been loaded, it's layout can be viewed by calling ``plate.layout``.

.. ipython:: python

    print plate.layout
	

This plate contains many empty rows and columns, which may be dropped for convenience.

.. ipython:: python
	
	plate = plate.dropna()
	print plate


Plotting
+++++++++++++++++
 
The entire plate can be plotted:

.. ipython:: python
	
	@savefig quick_hlog_plate.png width=4.5in
	out = hplate.plot(('FSC-A', 'Y2-A'))	


Examples 
------------------------------------------------

Counting the total number of events
++++++++++++++++++++++++++++++++++++++++++++++++


Calculating the standard deviation of data that passes a given gate
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


