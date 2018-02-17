from FlowCytometryTools.core import docstring

###############################
# Programmable Documentation  #
###############################

_doc_dict = dict(
    _graph_grid_layout="""\
xlim : None | 2-tuple
    If None automatic, otherwise specifies the xmin and xmax for the plot
ylim : None | 2-tuple
    If None automatic, otherwise specifies the ymin and ymax for the plot
row_label_xoffset : float
    Additional offset for the row labels in the x direction.
col_label_yoffset : float
    Additional offset for the col labels in the y direction.
hide_tick_labels : True | False
    Hides the tick mark labels.
hide_tick_lines : True | False
    Hides the tick marks.
hspace : float
    Horizontal space between subplots.
wspace : float
    Vertical space between subplots.
row_labels_kwargs : dict
    This dict is unpacked into the pylab.text function
    that draws the row labels.
col_labels_kwargs : dict
    This dict is unpacked into the pylab.text function
    that draws the column labels.""",

    _graph_grid_layout_returns="""\
(ax_main, ax_subplots)
    ax_main : reference to the main axes
    ax_subplots : matrix of references to the subplots (e.g., ax_subplots[0, 3] references
    the subplot in row 0 and column 3.)""",

_bases_filename_parser="""\
parser : ['name' | 'number' | 'read' | mapping | callable]

    Extracts a key from a filename.

    Later, this key is used by the position mapper to determine
    the location of the measurement in the measurement collection.

    * 'name' : Use the measurement name given in the file name.
       For example, '[whatever]_Well_C9_[blah].fcs' will get key 'C9'.
       The filename must look **exactly** like the template above.
    * 'number' : Use the number given in the file name.
       For example, '[some name].001.fcs' will get key 001.
       The filename must look **exactly** like the template above.
    * 'read' : Use the measurement ID specified in the metadata.
    * mapping : mapping (dict-like) from datafiles to keys.
    * callable : takes datafile name and returns key.""",

_bases_position_mapper="""\
position_mapper : [None, callable, mapping, 'name', 'row_first_enumerator', 'col_first_enumerator']

    Returns the coordinates (row, col) which correspond to the key.
    (The key is the key extracted from the filename by the parser.)

    For example, the key 'A1' corresponds to the matrix coordinates (0, 0).

        * None     : if None, then uses the same value as the parser
        * callable : gets key and returns position
        * mapping  : key:pos
        * 'name'   : parses things like 'A1', 'G12'
        * 'row_first_enumerator', 'name' : converts number to positions, going over rows first
        * 'col_first_enumerator' : converts number to positions, going over columns first.""",

_bases_ID= """\
ID : hashable
    Collection ID""",

_bases_data_files="""\
datafiles : str | iterable
    A set of data files containing the measurements.""",

_bases_ID_kwargs="""\
ID_kwargs: dict
    Additional parameters to be used when assigning IDs.
    Passed to '_assign_IDS_to_datafiles' method.""",

_gate_available_classes="""\
[:class:`~FlowCytometryTools.ThresholdGate` | :class:`~FlowCytometryTools.IntervalGate` | \
:class:`~FlowCytometryTools.QuadGate` | :class:`~FlowCytometryTools.PolyGate` | \
:class:`~FlowCytometryTools.core.gates.CompositeGate`]
""",

FCMeasurement_plot_pars="""\
gates : [None | Gate | iterable of Gate]
    Gate should be in {_gate_available_classes}.
    When supplied, the gates are drawn on the plot.
    The gates are applied by default.""",

FCMeasurement_transform_pars="""\
transform : ['hlog' | 'tlog' | 'glog' | callable]
    Specifies the transformation to apply to the data.

    * callable : a callable that does a transformation (should accept a number or array), or one of the supported named transformations.
direction : ['forward' | 'inverse']
    Direction of transformation.
channels : str | list of str | None
    Names of channels to transform.
    If None is given, all channels will be transformed.

    .. warning::
        Remember that transforming all channels does not always make sense. For example,
        when working with the time channel, one should probably keep the data as is.

return_all : bool
    True -  return all columns, with specified ones transformed.
    False - return only specified columns.
auto_range : bool
    If True data range (machine range) is automatically extracted from $PnR field of metadata.

    .. warning::
        If the data has been previously transformed its range may not match the $PnR value.
        In this case, auto_range should be set to False.
use_spln : bool
    If True th transform is done using a spline.
    See Transformation.transform for more details.
get_transformer : bool
    If True the transformer is returned in addition to the new Measurement.
args :
    Additional positional arguments to be passed to the Transformation.
kwargs :
    Additional keyword arguments to be passed to the Transformation.""",

FCMeasurement_transform_examples="""\
>>> trans = original.transform('hlog')
>>> trans = original.transform('tlog', th=2)
>>> trans = original.transform('hlog', d=log10(2**18), auto_range=False)
>>> trans = original.transform('hlog', r=1000, use_spln=True, get_transformer=True)
>>> trans = original.transform('hlog', channels=['FSC-A', 'SSC-A'], b=500).transform('hlog', channels='B1-A', b=100)""",

FCMeasurement_subsample_parameters="""\
key : [int | float | tuple | slice]
    When key is a single number, it specifies a number/fraction of events
    to use. Use the parameter 'order' to specify how to subsample
    the requested number/fraction of events.

    * int : specifies a number of events to use
    * float : specifies a fraction of events to use (a number between 0 and 1)
    * tuple : consists of two floats, each between 0 and 1. For example, key = (0.66666, 1.0) returns the last one third of events.
    * slice : applies a slice. For example, key = slice(10, 1000, 20) returns events with indexes [10, 30, 50, ...]

    .. note:

        When key is a tuple (2 floats) or a slice, the 'order' parameter is irrelevant.

order : ['random' | 'start' | 'end']
    Specifies which events to choose. This is only relevant
    when key is either an int or a float.

    * 'random' : chooses the events randomly (without replacement)
    * 'start' : subsamples starting from the start
    * 'end' : subsamples starting from the end

auto_resize : [False | True]
    If True, attempts to automatically control indexing errors.
    For example, if there are only 1000 events in the fcs sample,
    but the key is set to subsample 2000 events, then an error will be raised.
    However, with auto_resize set to True, the key will be adjusted
    to 1000 events.""",

graph_plotFCM_pars = """\
channel_names : [str | iterable of str]
    The name (or names) of the channels to plot.
    When one channel is specified, then a 1d histogram is plotted.
kind : ['scatter' | 'histogram']
    Specifies the kind of plot to use for plotting the data (only applies to 2D plots).
autolabel : [False | True]
    If True the x and y axes are labeled automatically.
colorbar : [False | True]
    Adds a colorbar. Only relevant when plotting a 2d histogram.
xlabel_kwargs : dict
    kwargs to be passed to the xlabel() command
ylabel_kwargs : dict
    kwargs to be passed to the ylabel() command
bins : int | ndarray | [ndarray]
    specifies how to bin histograms.

    * int : number of bins (autopilot!)
    * ndarray : for 1d histograms, e.g., linspace(-1000, 10000, 100)
    * [ndarray] : for 2d histograms, e.g., [linspace(-1000, 10000, 100), linspace(-1000, 10000, 100)]

    **CAUTION** when bins=int, the bin locations are determined
    automatically based on the data. This means that the bins
    can have different widths, depending on the range of the data.
    When plotting using FCCollection (FCPlate), the bin locations are set
    according to minimum and maximum values of data from across all the
    FCMeasurements. If this is confusing for you, just specify the
    bin locations explicitely.
    """,

common_plot_ax="""\
ax : [None | ax]
    Specifies which axis to plot on. If None, will plot
    on the current axis. """,

bases_OrderedCollection_grid_plot_pars="""\
ids : [None, list of IDs]
    If a list of IDs is provided, then
    only those measurements whose ID is in the list are plotted.
col_labels : [list of str, None]
    Labels for the columns. If None default labels are used.
row_labels : [list of str, None]
    Labels for the rows. If None default labels are used.
xlabel : str
   If not None, this is used to label the x axis of the top right most subplot.
ylabel : str
    If not None, this is used to label the y axis of the top right most subplot.
xlim : 2-tuple
    min and max x value for each subplot
    if None, the limits are automatically determined for each subplot
ylim : 2-tuple
    min and max y value for each subplot
    if None, the limits are automatically determined for each subplot""",

_containers_held_in_memory_warning="""\
.. warning::
    The new Collection will hold the data for **ALL** Measurements in memory!
    When analyzing multiple collections (e.g., multiple 96-well plates), it may be necessary
    to only work one collection at a time. Please refer to the tutorials to see how
    this can be done."""
)


doc_replacer = docstring.DocReplacer(**_doc_dict)
doc_replacer.replace()
