from GoreUtilities import docstring
from GoreUtilities.graph import _doc_dict as _gore_doc_dict

###############################
# Programmable Documentation  #
###############################

_doc_dict = dict(

_bases_filename_parser="""\
parser : ['name' | 'number' | 'read' | mapping | callable]

    Given a filename corresponding to a measurement,
    the parser extracts a key from the filenmae.

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
position_mapper : [None, callable, mapping, 'name', 'number']

    Accepts a key (which is extracted by the parser), and returns
    the coordinates in a matrix (measurement collection) that correspond
    to the key.

    For example, the key 'A1' corresponds to the matrix coordinate (0, 0).

        * None     : use the parser value, if it is a string.
        * callable : gets key and returns position
        * mapping  : key:pos
        * 'name'   : parses things like 'A1', 'G12'
        * 'number' : converts number to positions, going over rows first.""",

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
[:class:`~FlowCytometryTools.ThresholdGate`, :class:`~FlowCytometryTools.IntervalGate`, \
:class:`~FlowCytometryTools.QuadGate`, :class:`~FlowCytometryTools.PolyGate` ]""",

FCMeasurement_plot_pars="""\
transform : [valid transform | tuple of valid transforms | None]
    Transform to be applied to corresponding channels using the
    FCMeasurement.transform function.
    If a single transform is given, it will be applied to all plotted channels.
gates : [None | Gate | iterable of Gate]
    Gate should be in {_gate_available_classes}.
    When supplied, the gates are drawn on the plot.
    The gates are applied by default.
transform_first : bool
    Apply transforms before gating.""",

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
key : [int | float | slice]
    Use to specify how many events to choose or to provide a slice for indexing.

    * int : returns a random sample size key (sampling without replacement)
    * float : specifies a fraction of events to use (float must be between 0 and 1)
    * slice : applies a slice
how : ['random' | 'first' | 'last']
    Specifies which events to choose.

    * 'first' : chooses first number=key events.
    * 'last' : chooses last number=key events.
    * 'last' : chooses number=key events randomly (without replacement)

    Note: irrelevant when the key is a slice
auto_resize : [False | True]
    If True, attempts to automatically control indexing errors.
    For example, if there are only 1000 events in the fcs sample,
    but the key is set to subsample 2000 events, then an error willbe raised.
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
    kwargs to be passed to the ylabel() command""",

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


_doc_dict.update(_gore_doc_dict)

doc_replacer = docstring.DocReplacer(**_doc_dict)
doc_replacer.replace()
