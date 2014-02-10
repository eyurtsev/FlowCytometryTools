.. _tutorial:

.. currentmodule:: FlowCytometryTools


.. ipython:: python
    :suppress:

    import numpy as np
    np.set_printoptions(precision=4, suppress=True)

Loading a single FCS file
--------------------------

To get cracking, we need some flow cytometry data (i.e., .fcs files).  

A few sample flow cytometry data files have been bundled with this python package.

To locate these FCS files, enter the following:

.. ipython:: python

    import os, FlowCytometryTools;
    datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate01');
    datafile = os.path.join(datadir, 'RFP_Well_A3.fcs');

Alternatively, to analyze your own data, simply set the ``datafile`` variable to the path of your .fcs file.
(e.g., ``datafile=r'C:\data\my_very_awesome_data.fcs'``).

If ``datadir`` and ``datafile`` have been defined, we can proceed to load the data:

.. ipython:: python

    from pylab import * # Loads functions used for plotting

    # Loading the FCS data
	from FlowCytometryTools import FCMeasurement
    sample = FCMeasurement(ID='Test Plate', datafile=datafile)

**Windows Users**

Windows uses the backslash character (``\``) for paths. However, the backslash character is a special character in python
that is used for formatting strings. In order to specify paths correctly, you must precede the path with the character ``r``.

    * Good: ``datafile=r'C:\data\my_very_awesome_data.fcs'``
    * Bad: ``datafile='C:\data\my_very_awesome_data.fcs'``

**MacOS/Linux Users**

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

There's loads of useful information inside FCS files. If you're curious 
take a look at ``sample.meta``. 

.. ipython:: python
    
    print type(sample.meta)
    print sample.meta.keys()

The meaning of the fields in ``sample.meta`` is explained in the FCS format specifications.

Transformations
--------------------------

The presence of both very dim and very bright cell populations in flow
cytometry data can make it difficult to simultaneously visualize both
populations on the same plot. To address this problem, flow cytometry
analysis programs typically apply a transformation to the
data to make it easy to visualize and interpret properly.

Rather than having this transformation applied automatically and without your
knowledge, this package provides a few of the common transformations (e.g.,
hlog, tlog), but ultimately leaves it up to you to decide how to manipulate
your data.

As an example, let's apply the 'hlog' transformation to the ``Y2-A``, ``B1-A`` and
``V2-A`` channels, and save the transformed sample in ``tsample``.

.. ipython:: python

    tsample = sample.transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'])

Note that throughout the rest of the tutorial we'll always be working with hlog-transformed data.

.. note::
    For more details see the API documentation section.

    Also, you can read more about transformations here:
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

Programmatically
```````````````````````

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

Using the GUI
```````````````````````

You can launch the GUI for creating the gates, by calling the view() method of an ``FCMeasurement`` instance.

``tsample.view()``

.. warning::

    You have to install wxpython in order to use the GUI.

    Also, keep in mind that the GUI is still in early stages. Expect bugs.

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

What we'd like to do is to construct a flow cytometry plate object by loading all the '\*.fcs' files in a directory.

To do that, FCPlate needs to know where on the plate each file belongs; i.e.,
we need to tell it that the file 'My_awesome_data_Well_C9.fcs' corresponds to well 'C9', which corresponds to the third row and the ninth column on the plate.

The process by which the filename is mapped to a position on the plate is the following:

1. The filename is fed into a **parser** which extracts a key from it. 
   For example, given 'My_awesome_data_Well_C9.fcs', the parser returns 'C9'
2. The key is fed into a **position mapper** which returns a matrix position.
   For example, given 'C9' the position_mapper should return (2, 8). 
   The reason it's (2, 8) rather than (3, 9) is because counting starts from 0 rather than 1. (So 'A' corresponds to 0.)

Here's a summary table that'll help you decide what to do (depending on your file name format):

+-------------------------------------+-----------------+------------------------------------------------------------------------------------+
| File Name Format                    | parser          | Comments                                                                           |
+=====================================+=================+====================================================================================+
| '[whatever]_Well_C9_[blah].fcs'     | 'name'          |                                                                                    |
+-------------------------------------+-----------------+------------------------------------------------------------------------------------+
| '[blah]_someothertagC9_[blah].fcs'  | 'name'          | But to use must modify ID_kwargs (see API) for details                             |
+-------------------------------------+-----------------+------------------------------------------------------------------------------------+
| '[whatever].025.fcs'                | 'number'        | 001 -> A1, 002 -> B1, ... etc. i.e., advances by row first                         |
+-------------------------------------+-----------------+------------------------------------------------------------------------------------+
|   Some other naming format          | dict            | dict with keys = filenames, values = positions                                     |
+-------------------------------------+-----------------+------------------------------------------------------------------------------------+
|   Some other naming format          | function        | Provide a function that accepts a filename and returns a position (e.g., 'C9')     |
+-------------------------------------+-----------------+------------------------------------------------------------------------------------+


For the analysis below, we'll be using the 'name' parser since our files match that convention. OK. Let's try it out!

.. ipython:: python

	from FlowCytometryTools import FCPlate
    plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name').transform('hlog', channels=['Y2-A', 'B1-A'])

    # The line above is equivalent to the two steps below:
    # plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name')
    # plate = plate.transform('hlog', channels=['Y2-A', 'B1-A'])                                                                 


Let's see what data got loaded...

.. ipython:: python

    print plate

And just to confirm, let's look at the naming of our files to see that ``parser='name'`` should indeed work.

.. ipython:: python

    import os
    print os.path.basename(plate['A3'].datafile)
	

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

Counting using the counts method
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Use the ``counts`` method to count total number of events.

.. ipython:: python

    total_counts = plate.counts()
    print total_counts

Let's count the number of events that pass a certain gate:

.. ipython:: python

    y2_counts = plate.gate(y2_gate).counts()
    print y2_counts

What about the events that land outside the y2_gate?

.. ipython:: python

    outside_of_y2_counts = plate.gate(~y2_gate).counts()
    print outside_of_y2_counts


Counting on our own
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To learn how to do more complex calculations, let's start by writing our
own counting function. At the end of this, we better get the
same result as was produced using the ``counts`` method above.

Here's the function:

.. ipython:: python
    
    def count_events(well):
        """ Counts the number of events inside of a well. """
        data = well.get_data()
        count = data.shape[0]
        return count

Let's check that it works on a single well.

.. ipython:: python

    print count_events(plate['A3'])


Now, to use it in a calculation we need to feed it to the ``apply`` method.
Like this:

.. ipython:: python

    print plate['A3'].apply(count_events)

The ``apply`` method is a functional, which is just a fancy way of saying
that it accepts functions as inputs. If you've got a function that can 
operate on a well (like the function ``count_events``), you can feed it into the ``apply``
method. Check the API for the ``apply`` method for more details.

Anyway, the ``apply`` method is particularly useful because it works on plates.

.. ipython:: python

    total_counts_using_our_function = plate.apply(count_events)
    print type(total_counts_using_our_function)
    print total_counts_using_our_function

Holy Rabbit! That was smokin' hot output!

First, for wells without data, a ``nan`` was produced.
Second, the output that was returned is a DataFrame. 

Also, as you can see the total counts we computed (``total_counts_using_our_function``)
agrees with the counts computed using the ``counts`` methods in the previous example.

Now, let's apply a gate and count again.

.. ipython:: python

    print plate.gate(y2_gate).apply(count_events)

Calculating median fluorescence
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Ready for some more baking?

Let's calculate the median Y2-A fluorescence.

.. ipython:: python
    
    def calculate_median_rfp(well):
        """ Calculates the median on the RFP channel. """
        data = well.get_data()
        return data['Y2-A'].median()

The median rfp fluorescence for all events in well 'A3'.

.. ipython:: python
    
    print calculate_median_rfp(plate['A3'])

The median rfp fluorescence for all events in the plate is:

.. ipython:: python

    print plate.apply(calculate_median_rfp)

The median rfp fluorescence for all events that pass the y2_gate is:

.. ipython:: python

    print plate.gate(y2_gate).apply(calculate_median_rfp)
