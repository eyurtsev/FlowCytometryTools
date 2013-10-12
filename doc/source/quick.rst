.. _quick:

.. currentmodule:: FlowCytometryTools


.. ipython:: python
    :suppress:

    import numpy as np
    from numpy import shape, log, where, nan
    from pylab import figure, cm, title, ylim, xlim, xlabel, ylabel, subplot

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

To get cracking, we need some flow cytometry data (i.e., .fcs files).  
We'll use the sample fcs files provided with this package.  
To analyze your own data, simply set the ``datafile`` variable to the path of your .fcs file.
(e.g., ``datafile=r'C:\data\my_very_awesome_data.fcs'``)


.. ipython:: python

	from FlowCytometryTools import FCMeasurement
    sample = FCMeasurement(ID='Test Plate', datafile=datafile)

.. note::
    **Windows Users**

    Windows uses a backslash (``\``) for indicating paths.  The backslash character is a special character in python.  
    In order to specify paths correctly, you must precede the path with the character ``r``.

    Good: ``datafile=r'C:\data\my_very_awesome_data.fcs'``

    Bad: ``datafile='C:\data\my_very_awesome_data.fcs'``

    **Everyone else**

    Your system uses the forward slash (``/``), which is a regular character, so there won't be any problems.


Channel Names
++++++++++++++++++++++++++++

Want to know which channels were measured? No problem.

.. ipython:: python

    print sample.channel_names

.. hint::

    Full information about the channels is available in ``sample.channels``.

Meta data
++++++++++++++++++++++++++++

There's loads of useful information in FCS files. If you're curious 
take a look at ``sample.meta``. 

.. ipython:: python
    
    print type(sample.meta)
    print sample.meta.keys()

The meaning of the fields in ``sample.meta`` is explained in the FCS format specifications.

Transformations
--------------------------

If you'd like to see your data (and be able to make sense of it), you'll *likely* need to transform it. 

Let's apply an 'hlog' transformation to the ``Y2-A``, ``B1-A`` and ``V2-A`` channels, 
and save the transformed sample in ``tsample``.

.. ipython:: python

    tsample = sample.transform('hlog', ('Y2-A', 'B1-A', 'V2-A'))

.. note::
    You can read more about transformations here:
        * Bagwell. Cytometry Part A, 2005.
        * Parks, Roederer, and Moore. Cytometry Part A, 2006.
        * Trotter, Joseph. In Current Protocols in Cytometry. John Wiley & Sons, Inc., 2001.

Plotting
--------------------------

1d histograms
++++++++++++++++++++++++++

Let's start with 1d histograms. 

.. ipython:: python

    figure();
	@savefig 1d_plot.png width=4.5in
    tsample.plot('Y2-A', bins=100);


The plot function accepts all the same arguments as does the matplotlib histogram function.

.. ipython:: python

    figure();
	@savefig 1d_plot_B.png width=4.5in
    tsample.plot('Y2-A', bins=100, alpha=0.7, color='green', normed=1);


2d histograms
++++++++++++++++++++++++++

If you feed the plot function with the names of two channels, you'll get a 2d histogram.

.. ipython:: python

    figure();
	@savefig 2d_plot_A.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A']);

As with 1d histograms, the plot function accepts all the same arguments as does the matplotlib histogram function.

.. ipython:: python

    figure();
	@savefig 2d_plot_B.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A'], cmap=cm.Oranges, colorbar=False);

2d scatter plots
++++++++++++++++++++++

To create a scatter plot, provide the argument ``kind='scatter`` to the plot command.

This makes the plot function behave like the matplotlib scatter function (and accept all the same arguments).

.. ipython:: python

    figure();
	@savefig 2d_scatter_plot_A.png width=4.5in
    tsample.plot(['B1-A', 'Y2-A'], kind='scatter', color='red', s=1, alpha=0.3);


Calculations
---------------------

.. ipython:: python

    data = tsample.get_data()
    print data

That's right. Your data is a pandas DataFrame, which means that you've got
the entire power of pandas at your fingertips!

.. ipython:: python

    print data['Y2-A'].describe()


Want to know how many events are in the data?

.. ipython:: python

    print data.shape[0]

Want to calculate the median fluorescence level measured on the ``Y2-A`` channel?

.. ipython:: python

    print data['Y2-A'].median()


Gating
--------------------------

First, we need to load the gates from the library.

.. ipython:: python

    from FlowCytometryTools import ThresholdGate, PolyGate

Creating Gates
+++++++++++++++++++++++

To create a gate you need to provide the following information:

* set(s) of coordinates
* name(s) of channel(s) 
* region

For example, here's a gate that passes events with a Y2-A (RFP) value *above* the 1000.0.

.. ipython:: python

    y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')


While we're at it, here's another gate for events with a B1-A value (CFP) above 2000.0.

.. ipython:: python

    b1_gate = ThresholdGate(2000.0, 'B1-A', region='above')

GUI for creating gates 
++++++++++++++++++++++++

You can launch the GUI for creating the gates, by calling the view() method.

.. note::

    Try ``tsample.view()``

    **ATTENTION**

    You have to install wxpython in order to use the GUI.

    Also, keep in mind that the GUI is still in early stages.

    If it works for you great, if not keep checking for updates! ;)

Plotting Gates
+++++++++++++++++

.. ipython:: python

    figure();
    ax1 = subplot(111);
    tsample.plot('Y2-A', gates=[y2_gate], apply_gates=False, bins=100);
	@savefig gate_A_plot.png width=4.5in
    title('All events');

    figure();
    ax2 = subplot(111, sharey=ax1, sharex=ax1);
    tsample.plot('Y2-A', gates=[y2_gate], apply_gates=True, bins=100, color='y');
	@savefig gate_B_plot.png width=4.5in
    title('Events in gate only');

Applying Gates
+++++++++++++++++

.. ipython:: python

    gated_sample = tsample.gate(y2_gate)
    print gated_sample.get_data().shape[0]

The ``gated_sample`` is also an FCMeasurement, so it supports the
same routines as the ungated sample. For example, we can plot it:

.. ipython:: python

    figure();
    ax1 = subplot(111);
    tsample.plot('Y2-A', color='gray', bins=100);
	@savefig gate_C_plot.png width=4.5in
    title('All events in tsample');

    figure();
    ax2 = subplot(111, sharey=ax1, sharex=ax1);
    gated_sample.plot('Y2-A', color='y', bins=100);
	@savefig gate_D_plot.png width=4.5in
    title('All events in the gated sample');

Working with plates
---------------------

For high-throughput analysis of flow cytometery data,
loading single FCS files is silly.

Instead, we provided you with the awesome ``FCPlate`` class!

Loading Data
++++++++++++++++++

Let's construct a flow cytometry plate object by loading all the '\*.fcs' files in a directory.

.. ipython:: python

	from FlowCytometryTools import FCPlate
    plate = FCPlate.from_dir(ID='Demo Plate', path=datadir).transform('hlog', channels=('Y2-A', 'B1-A'))

    # The line above is equivalent to the two steps below:
    # plate = FCPlate.from_dir(ID='Demo Plate', path=datadir)
    # plate = plate.transform('hlog', channels=('Y2-A', 'B1-A'))                                                                 

.. note:: Parsers
    TODO

Let's see what data got loaded...

.. ipython:: python

    print plate
	

This plate contains many empty rows and columns, which may be dropped for convenience.

.. ipython:: python
	
	plate = plate.dropna()
	print plate


Plotting
+++++++++++++++++

1d histograms
=================

 
.. ipython:: python

    figure();
	@savefig plate_plot_A.png width=4.5in
    plate.plot('Y2-A', bins=100);

2d histograms
=================

.. ipython:: python

    figure();
	@savefig plate_plot_B.png width=4.5in
    plate.plot(('B1-A', 'Y2-A'), bins=100);

Accessing Single Wells
++++++++++++++++++++++++

FCPlate supports indexing to make it easier to work with single wells.

.. ipython:: python

    figure();
    print plate['A3']
	@savefig plate_indexing_A.png width=4.5in
    plate['A3'].plot('Y2-A', bins=100);



Examples
------------------------------------------------

Counting total number of events
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Let's write code to count the total number of events in each well of the plate.

.. ipython:: python
    
    def count_events(well):
        """ Counts the number of events inside of a well. """
        data = well.get_data()
        count = data.shape[0]
        return count

Before we use this function on a plate, we have to check that it works
on a single well.

.. ipython:: python

    print count_events(plate['A3'])

Alternatively, we could have used the ``apply`` method:

.. ipython:: python

    print plate['A3'].apply(count_events)

The really nice thing about the ``apply`` method is that it works on plate:

.. ipython:: python

    output = plate.apply(count_events)
    print type(output)
    print output

That's some real sexy output that we got out of the ``apply`` function!

First, for wells without data, a ``nan`` was produced.
Second, the output that was returned is a DataFrame. 
(Check the example below to see why that's so cool.)


Counting events passing through a gate
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Let's build on top of the previous example and count the number
of events that pass a given gate.

.. ipython:: python
    
    def count_events_in_gate(well, gate):
        """ Counts the number of events in fcs_sample that pass the given gate. """
        data = well.gate(gate).get_data()
        count = data.shape[0]
        return count

Let's test this out on a a single well:

.. ipython:: python

    y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')
    print count_events_in_gate(plate['A3'], y2_gate)

Here's tricky part:

The ``apply`` method only accepts functions of a single argument 
(i.e., the well on which to compute). 

However, the function we have accepts two arguments: well and gate.

We need to provide the gate argument before we pass the function to ``apply``.

To do that let's use a lambda function.

.. ipython:: python

    count_in_y2_gate = lambda well : count_events_in_gate(well, y2_gate)

    print count_in_y2_gate(plate['A3'])

    print plate['A3'].apply(count_in_y2_gate) # Now this works!! Woohoo!!

OK, now we can use this function to count the number of events that pass
the gate across the entire plate.


.. ipython:: python

    output = plate.apply(count_in_y2_gate)
    print output

Now, amongst one of the cool things about output being a pandas DataFrame is that we can plot it:

.. ipython:: python

    figure();

    output.plot();
    xlabel('Row');
	@savefig example_A_dataframe.png width=4.5in
    ylabel('Counts');

Calculating median fluorescence
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Ready for some more baking?

Let's calculate the median Y2-A fluorescence.

.. ipython:: python
    
    def calculate_median_rfp(well, gate):
        """ Counts the number of events in fcs_sample that pass the given gate. """
        if gate is not None:
            data = well.gate(gate).get_data()
        else:
            data = well.get_data()

        return data['Y2-A'].median()

The median rfp fluorescence for all events in well 'A3'.

.. ipython:: python
    
    print calculate_median_rfp(plate['A3'], None)


The median rfp fluorescence for all events in the plate is:

.. ipython:: python

    calculate_overall_median_rfp = lambda well : calculate_median_rfp(well, None)

    print plate.apply(calculate_overall_median_rfp)

The median rfp fluorescence for all events that pass the y2_gate is:

.. ipython:: python

    calculate_in_y2_gate_median_rfp = lambda well : calculate_median_rfp(well, y2_gate)

    print plate.apply(calculate_in_y2_gate_median_rfp)

