"""" @author: Eugene Yurtsev @date 2013-07-25

Defines gates that operate on DataFrames.

API:
    DataFrame -- pandas object
    gate1 -- a polygon gate.

Gates:
    ThresholdGate
    IntervalGate
    QuadGate
    PolyGate
"""
import numpy
import pylab as pl
from matplotlib.path import Path

from FlowCytometryTools.core.common_doc import doc_replacer
from FlowCytometryTools.core.utils import to_list

doc_replacer.update(_gate_pars_name="""\
name : str
    The gate's name.""")
doc_replacer.update(_gate_pars_1_channel="""\
channel : str
    Defines the channel name.""")

doc_replacer.update(_gate_pars_2_channels=
                    """channels : ['channel 1 name', 'channel 2 name']
                        Defines the names of the channels""")

doc_replacer.update(_gate_plot_doc=
                    """Plots the gate.

                    .. warning:
                        The plot function does not check that your
                        axis correspond to the correct channels.

                    Parameters
                    ----------
                    ax : axes to use for plotting the gate on
                    flip : boolean
                        If True, draws the interval
                        along the y-axis instead of along the x-axis

                    Returns
                    -------
                    Reference to created artists.""")


class _ComposableMixin(object):
    """ A mixin' class that enables to compose gates using logic elements. """

    def __and__(self, other):
        return CompositeGate(self, 'and', other)

    def __xor__(self, other):
        return CompositeGate(self, 'xor', other)

    def __or__(self, other):
        return CompositeGate(self, 'or', other)

    def __invert__(self):
        return CompositeGate(self, 'invert')


class Gate(_ComposableMixin):
    """ Defines common interface for specific implementations of the gate classes. """
    unnamed_gate_num = 1

    def __init__(self, vert, channels, region, name=None):
        self.vert = vert
        channels = to_list(channels)
        self.channels = channels

        if name == None:
            self.name = "Unnamed Gate {0}".format(Gate.unnamed_gate_num)
            Gate.unnamed_gate_num += 1
        else:
            self.name = name

        self.region = region
        self.validate_input()

    def validate_input(self):
        """ Optional method to be defined by derived class
        to check whether user input was valid. """
        pass

    def __repr__(self):
        return """Gate Type: {0}
               \tVertices: {1}
               \tChannel(s): {2}
               \tName: {3}
                """.format(self.__class__, self.vert, self.channels, self.name)

    def __str__(self):
        return self.__repr__()

    def __call__(self, dataframe, region=None):
        """
        Filters the dataframe, keeping only events that pass the gate.

        Parameters
        --------------
        dataframe : DataFrame
        region : None, optional
            If specified, the gate region is updated to the given region.
        """
        if region is not None:
            self.region = region

        for c in self.channels:
            if c not in dataframe:
                raise ValueError(
                    'Trying to filter based on channel {channel}, which is not present in the data.'.format(
                        channel=c))

        idx = self._identify(dataframe)

        return dataframe[idx]

    def _find_orientation(self, ax_channels):
        ax_channels = to_list(ax_channels)
        c = self.channels[0]
        if ax_channels is not None:
            try:
                i = ax_channels.index(c)
                if i == 0:
                    flip = False
                else:
                    flip = True
            except ValueError:
                raise Exception("""Trying to plot gate that is defined on channel {0},
                                but figure axis correspond to channels {1}""".format(c,
                                                                                     ax_channels))
        if len(self.channels) == 2:
            c = self.channels[1]
            if c not in ax_channels:
                raise Exception("""Trying to plot gate that is defined on channel {0},
                                but figure axis correspond to channels {1}""".format(c,
                                                                                     ax_channels))
        return flip

    def plot(self, **kwargs):
        """ Plots the gate. Must be specified in derived class. """
        raise NotImplementedError('Plotting is not yet supported for this gate type.')

    def _identify(self, dataframe):
        """ Returns a list of indexes corresponding to events that pass the gate. """
        raise NotImplementedError

    @property
    def region(self):
        """ The region of the gate that passes events. """
        return self._region

    @region.setter
    def region(self, value):
        if value.lower() in self._region_options:
            self._region = value.lower()
        else:
            raise ValueError(
                "region must be one of the following: {0}".format(self._region_options))


class ThresholdGate(Gate):
    @doc_replacer
    def __init__(self, threshold, channel, region, name=None):
        """
        Passes all events above or below a given threshold.

        Parameters
        ----------
        threshold : float
            Location of the gate
        {_gate_pars_1_channel}
        region : ['above', 'below']
            If 'above', the gate only passes through data that lies above the threshold.
        {_gate_pars_name}
        """

        #: Possible regions
        self._region_options = ('above', 'below')

        super(ThresholdGate, self).__init__(threshold, channel, region, name)

    def _identify(self, dataframe):
        """ Identifies which of the data points in the dataframe pass the gate. """
        idx = dataframe[self.channels[0]] >= self.vert  # Get indexes that are above threshold

        if self.region == 'below':
            idx = ~idx

        return idx

    @doc_replacer
    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        {_gate_plot_doc}
        """
        if ax == None:
            ax = pl.gca()

        if ax_channels is not None:
            flip = self._find_orientation(ax_channels)

        plot_func = ax.axes.axhline if flip else ax.axes.axvline

        kwargs.setdefault('color', 'black')
        return plot_func(self.vert, *args, **kwargs)


class IntervalGate(Gate):
    @doc_replacer
    def __init__(self, vert, channel, region, name=None):
        """
        Passes all events either inside or outside the given interval.

        Parameters
        ----------
        vert : tuple
            Tuple describes the interval (xmin, xmax)
        {_gate_pars_1_channel}
        region : ['in', 'out']
            If 'in', the gate only passes through data that lies inside the interval.
        {_gate_pars_name}
        """
        self._region_options = ('in', 'out')
        super(IntervalGate, self).__init__(vert, channel, region, name)

    def validate_input(self):
        """Raise appropriate exception if gate was defined incorrectly."""
        if self.vert[1] <= self.vert[0]:
            raise ValueError(u'{} must be larger than {}'.format(self.vert[1], self.vert[0]))

    def _identify(self, dataframe):
        """Return bool series which is True for indexes that 'pass' the gate"""
        idx = ((dataframe[self.channels[0]] <= self.vert[1]) &
               (dataframe[self.channels[0]] >= self.vert[0]))

        if self.region == 'out':
            idx = ~idx

        return idx

    @doc_replacer
    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        {_gate_plot_doc}
        """
        if ax == None:
            ax = pl.gca()

        if ax_channels is not None:
            flip = self._find_orientation(ax_channels)

        plot_func = ax.axes.axhline if flip else ax.axes.axvline

        kwargs.setdefault('color', 'black')
        a1 = plot_func(self.vert[0], *args, **kwargs)
        a2 = plot_func(self.vert[1], *args, **kwargs)

        return (a1, a2)


class QuadGate(Gate):
    @doc_replacer
    def __init__(self, vert, channels, region, name=None):
        """
        Passes events in a given quadrant of a 2d-plot.

        Parameters
        ----------
        vert : tuple
            A tuple of length 2: (x_center, y_center)
            Specifies the center of the quad gate.
        {_gate_pars_2_channels}
        region : ['top left', 'top right', 'bottom left', 'bottom right']
            For example, if 'top left', the gate only passes through data that lies in the top left region.
        {_gate_pars_name}
        """
        self._region_options = ('top left', 'top right', 'bottom left', 'bottom right')
        super(QuadGate, self).__init__(vert, channels, region, name)

    def _identify(self, dataframe):
        """
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe : DataFrame
        """
        ##
        # TODO Fix this implementation. (i.e., why not support just 'left')
        # At the moment this implementation won't work at all.
        # The logic here can be simplified.
        id1 = dataframe[self.channels[0]] >= self.vert[0]
        id2 = dataframe[self.channels[1]] >= self.vert[1]

        if 'left' in self.region: id1 = ~id1
        if 'bottom' in self.region: id2 = ~id2

        idx = id1 & id2

        if 'out' in self.region:
            idx = ~idx

        return idx

    @doc_replacer
    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        {_gate_plot_doc}
        """
        if ax == None:
            ax = pl.gca()

        kwargs.setdefault('color', 'black')

        if ax_channels is not None:
            flip = self._find_orientation(ax_channels)

        if not flip:
            a1 = ax.axes.axvline(self.vert[0], *args, **kwargs)
            a2 = ax.axes.axhline(self.vert[1], *args, **kwargs)
        else:
            a1 = ax.axes.axvline(self.vert[1], *args, **kwargs)
            a2 = ax.axes.axhline(self.vert[0], *args, **kwargs)

        return (a1, a2)


class PolyGate(Gate):
    @doc_replacer
    def __init__(self, vert, channels, region='in', name=None):
        """
        Passes all events that are either inside or outside the polygon.

        Parameters
        ----------
        vert : list of 2-tuples
            [(x1, y1), (x2, y2), (x3, y3)]
            Each 2-tuple describes the location of a vertex.
        {_gate_pars_2_channels}
        region : ['in', 'out']
            If 'in', the gate only passes through data that lies inside the interval.
        {_gate_pars_name}
        """
        self._region_options = ('in', 'out')
        super(PolyGate, self).__init__(vert, channels, region, name)

    def _identify(self, dataframe):
        """
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe : DataFrame
        """
        path = Path(self.vert)
        idx = path.contains_points(dataframe.filter(self.channels))

        if self.region == 'out':
            idx = ~idx

        return idx

    @doc_replacer
    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        {_gate_plot_doc}
        """
        if ax == None:
            ax = pl.gca()

        if ax_channels is not None:
            flip = self._find_orientation(ax_channels)
        if flip:
            vert = [v[::-1] for v in self.vert]
        else:
            vert = self.vert
        kwargs.setdefault('fill', False)
        kwargs.setdefault('color', 'black')
        poly = pl.Polygon(vert, *args, **kwargs)
        return ax.add_artist(poly)


class CompositeGate(_ComposableMixin):
    """
    Defines a composite gate that is generated by the logical addition of one or more gates.

    Examples
    --------

    You can create the union of two gates by combining them with how='or'.

    >>> union_gate = CompositeGate(gate1, 'or', gate2)

    However,

    There is a shorthand to do the same operation

    >>> union_gate = gate1 | gate2

    Similarly, if you wanted the intersection:

    >>> intersection_gate = CompositeGate(gate1, 'and', gate2)

    With the shorthand

    >>> intersection_gate = gate1 & gate2

    As another example, let's invert a gate.

    The longway:

    >>> inverted_gate = CompositeGate(gate1, 'invert')

    The shortway:

    >>> inverted_gate = ~gate1

    .. warning::

        When using the shorthand notation you must use the syntax '~', '&', '|'.
        Do **NOT** use 'and', 'or', 'not'.
    """

    def __init__(self, gate1, how, gate2=None):
        """
        Instead of using this class directly to create composite gates, it is recommended
        you use the shorthand syntax presented directly above.

        Parameters
        ----------

        gate1 : subclass of Gate
        how : ['and' | 'or' | 'invert' | 'xor']
            Describes how to combine the gates
        gate2 : subclass of Gate
            Need to specify is how is anything but 'not'.

        """
        self.gates = [gate1]
        if gate2 is not None:
            self.gates.append(gate2)
        self.how = how

    @property
    def name(self):
        if len(self.gates) == 1:
            gate = self.gates[0]
            return '~{0}'.format(gate.name)
        else:
            return '{0} {1} {2}'.format(self.gates[0].name, self.how, self.gates[1].name)

    def __str__(self):
        return self.name

    def _identify(self, dataframe):
        idx = [gate._identify(dataframe) for gate in self.gates]

        if self.how == 'and':
            function = numpy.logical_and
        elif self.how == 'or':
            function = numpy.logical_or
        elif self.how == 'invert':
            function = numpy.logical_not
        elif self.how == 'xor':
            function = numpy.logical_xor
        else:
            supported_values = ('and', 'or', 'invert', 'xor')
            raise ValueError(
                "Unsupported value for how. how must be in ({0})".format(supported_values))

        return function(*idx)

    def __call__(self, dataframe):
        idx = self._identify(dataframe)
        return dataframe[idx]

    @doc_replacer
    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        {_gate_plot_doc}
        """
        for gate in self.gates:
            gate.plot(flip=flip, ax_channels=ax_channels, ax=ax, *args, **kwargs)
