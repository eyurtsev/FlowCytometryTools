.. _tutorial:

.. currentmodule:: FlowCytometryTools


.. ipython:: python
    :suppress:

    import numpy as np
    np.set_printoptions(precision=4, suppress=True)

Specifying paths to FCS data
----------------------------

To get cracking, we need some flow cytometry data (i.e., .fcs files). A few FCS data files have been bundled with this python package. To use these files, enter the following in your ipython terminal:

.. ipython:: python

    import FlowCytometryTools
    from FlowCytometryTools import test_data_dir, test_data_file

    datadir = test_data_dir
    datafile = test_data_file

``datadir`` will point to a directory containing flow cytometry data while ``datafile`` will point
to a specific FCS file. 

To analyze your own data, simply set the 'datafile' variable to the path of your .fcs file:

    >>> datafile=r'C:\data\my_very_awesome_data.fcs'

|

*Windows Users* Windows uses the backslash character ('\') for paths. However, the backslash character is a special character in python that is used for formatting strings. In order to specify paths correctly, you must precede the path with the character 'r'.

    Good: 

    >>> datafile=r'C:\data\my_very_awesome_data.fcs'

    Bad: 
    
    >>> datafile='C:\data\my_very_awesome_data.fcs'


Working with individual FCS files
---------------------------------

Below is a brief description, for more information see :class:`FCMeasurement`.

Loading the file
++++++++++++++++++++++++++++

Once ``datadir`` and ``datafile`` have been defined, we can proceed to load the data:

.. ipython:: python

	from FlowCytometryTools import FCMeasurement
    sample = FCMeasurement(ID='Test Sample', datafile=datafile)

Channel Information
++++++++++++++++++++++++++++

Want to know which channels were measured? No problem.

.. ipython:: python

    print sample.channel_names

.. ipython:: python

    print sample.channels

Full Meta Data
++++++++++++++++++++++++++++

In addition to the raw data, the FCS files contain "meta" information about the
measurements, which may be useful for data analysis. You can access this
information using the `meta` property, which will return to you a python
dictionary. The meaning of the fields in meta data is explained in the FCS
format specifications (google for the specification).

.. ipython:: python
    
    print type(sample.meta)
    print sample.meta.keys()
    print sample.meta['$SRC']

Accessing Raw Data
+++++++++++++++++++++++++++

The data is accessible as a `pandas.DataFrame <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`_.

.. ipython:: python
    
    print type(sample.data)
    print sample.data[['Y2-A', 'FSC-A']][:10]


If you do not know how to work with DataFrames, you can get the underlying numpy array using the values property.

.. ipython:: python
    
    print type(sample.data.values)
    print sample.data[['Y2-A', 'FSC-A']][:10].values

Of course, working directly with a pandas DataFrame is very convenient. For example,

.. ipython:: python

    data = sample.data
    print data['Y2-A'].describe()

Want to know how many events are in the data?

.. ipython:: python

    print data.shape[0]

Want to calculate the median fluorescence level measured on the ``Y2-A`` channel?

.. ipython:: python

    print data['Y2-A'].median()

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

    tsample = sample.transform('hlog', channels=['Y2-A', 'B1-A', 'V2-A'], b=500.0)

In the hlog transformation, the parameter `b` controls the location where the transformation shifts from
linear to log. The optimal value for this parameter depends on the range of your data. For smaller ranges, 
try smaller values of `b`. So if your population doesn't show up well, just adjust `b`.

For more information see :meth:`FCMeasurement.transform`, :meth:`FlowCytometryTools.core.transforms.hlog`.

Throughout the rest of the tutorial we'll always be working with hlog-transformed data.

.. note::

    For more details see the API documentation section.

    You can read more about transformations here:
        * Bagwell. Cytometry Part A, 2005.
        * Parks, Roederer, and Moore. Cytometry Part A, 2006.
        * Trotter, Joseph. In Current Protocols in Cytometry. John Wiley & Sons, Inc., 2001.

Compensation and custom transformations
++++++++++++++++++++++++++++++++++++++++++

If you want to compensate your data or perform a custom transformation 
there's an example in the `gallery <gallery.html>`_.

**HINT**: It's very easy!


Plotting
--------------------------

Let's import matplotlib's plotting functions.

.. ipython:: python

    from pylab import *

For more information see :meth:`FCMeasurement.plot`.

1d histograms
++++++++++++++++++++++++++

.. ipython:: python

    figure();
	@savefig 1d_plot.png width=4.5in
    tsample.plot('Y2-A', bins=100);

.. ipython:: python

    figure();
    grid(True)
	@savefig 1d_plot_prettier.png width=4.5in
    tsample.plot('Y2-A', color='green', alpha=0.7, bins=100);

2d histograms
++++++++++++++++++++++++++

If you provide the plot function with the names of two channels, you'll get a 2d histogram.

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


Gating
--------------------------

See the `API <api.html#gates>`_ for a list of available gates.

Let's import a few of those gates.

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

Let's create a :class:`ThresholdGate` that passes events with a Y2-A (RFP) value *above* the 1000.0.

.. ipython:: python

    y2_gate = ThresholdGate(1000.0, 'Y2-A', region='above')


While we're at it, here's another gate for events with a B1-A value (CFP) above 2000.0.

.. ipython:: python

    b1_gate = ThresholdGate(2000.0, 'B1-A', region='above')

Using the GUI
```````````````````````

You can launch the GUI for creating the gates, by calling the view_interactively() method of an ``FCMeasurement`` instance.

>>> tsample.view_interactively()

.. warning::

    wxpython must be installed in order to use the GUI. (It may already be installed, so just try it out.)

    Please note that there's no way to apply transformations through the GUI, so
    view samples through the view_interactively method. (Don't load new FCS files directly from the GUI,
    if you need those files transformed.)

Plotting Gates
+++++++++++++++++

.. ipython:: python

    figure();
    tsample.plot('Y2-A', gates=[y2_gate], bins=100);
	@savefig gate_A_plot.png width=4.5in
    title('Gate Plotted');

Applying Gates
+++++++++++++++++

.. ipython:: python

    gated_sample = tsample.gate(y2_gate)
    print gated_sample.get_data().shape[0]

The ``gated_sample`` is also an instance of :class:`FCMeasurement`, so it supports the
same routines as does the ungated sample. For example, we can plot it:

.. ipython:: python

    figure();
    gated_sample.plot('Y2-A', color='y', bins=100);
	@savefig gated_sample_only_plot.png width=4.5in
    title('Gated Sample');

Let's compare the gated and ungated side by side.

.. ipython:: python

    figure();
    subplots_adjust(hspace=0.4)
    ax1 = subplot(211);
    tsample.plot('Y2-A', color='gray', bins=100, gates=[y2_gate]);
    title('Original Sample');

    ax2 = subplot(212, sharey=ax1, sharex=ax1);
    gated_sample.plot('Y2-A', color='y', bins=100, gates=[y2_gate]);
	@savefig gate_D_plot.png width=4.5in
    title('Gated Sample');

Combining gates
+++++++++++++++++

Gates can be inverted and combined together. See :class:`FlowCytometryTools.core.gates.CompositeGate`.

Working with plates
---------------------

For high-throughput analysis of flow cytometery data,
loading single FCS files is silly. Don't be silly!

Instead, we provided you with the awesome `FCPlate <api.html#fcplate>`_ class (also called :class:`FCOrderedCollection`).

Loading Data
++++++++++++++++++++++++++

The code below loads two FCS samples and shows two different methods of placing them on a plate container.

.. ipython:: python

	from FlowCytometryTools import FCPlate

    sample1 = FCMeasurement('B1', datafile=datafile); 
    sample2 = FCMeasurement('D2', datafile=datafile);

    # Use the samples ID as their position on a plate:
    plate1 = FCPlate('demo plate', [sample1, sample2], 'name', shape=(4, 3))
    print plate1

Alternatively, one can specify the sample positions independent of the samples IDs using a dictionary:

.. ipython:: python

    plate2 = FCPlate('demo plate', {'C2' : sample1, 'C3' : sample2}, 'name', shape=(4, 3))
    print plate2

    print plate2['C2']

Having overwritten the default mapping based on the samples ID, we now have to access ``sample1`` using the key ``C2``. So the command ``plate['C2']`` should return sample1 (whose ID should still remain ``B1``).

.. ipython:: python

    plate3 = FCPlate('demo plate', {3 : sample1, 4 : sample2}, 'row_first_enumerator', shape=(4, 3))
    print plate3

    print plate3[3]


.. note::

    Below we show a much faster way of loading data into a plate format. This method should make life simpler for most users by removing a bunch of boilerplate code. So keep on reading!

Loading Data (better way)
+++++++++++++++++++++++++

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


For the analysis below, we'll be using the 'name' parser since our files match that convention. OK. Let's try it out:

.. ipython:: python

	from FlowCytometryTools import FCPlate

    plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name')
    plate = plate.transform('hlog', channels=['Y2-A', 'B1-A'])                                                                 

Let's see what data got loaded.

.. ipython:: python

    print plate

And just to confirm, let's look at the naming of our files to see that ``parser='name'`` should indeed work.

.. ipython:: python

    import os
    print os.path.basename(plate['A3'].datafile)

This plate contains many empty rows and columns. The method :meth:`FCPlate.dropna` allow us to drop empty rows and columns for convenience:

.. ipython:: python
	
	plate = plate.dropna()
	print plate


Plotting
+++++++++++++++++

Please import matplotlib's plotting functions if you haven't yet...

.. ipython:: python

    from pylab import *

For more information see :meth:`FCPlate.plot`.

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
    plate.plot(('B1-A', 'Y2-A'), bins=100, wspace=0.2, hspace=0.2);

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

Holy Rabbit! 

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

