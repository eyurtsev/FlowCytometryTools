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

TODO
----------
* Update documentation.
* Add checks for correct user input:
        if self.__class__ is isinstance(PolyGate):
            if len(vert) < 2:
                raise Exception('vert must be a list of 2-tuples [(x1, y1), (x2, y2), (x3, y3)]')
            if len(channels) != 2 or channel[0] == channel[1]:
                raise Exception('You must define 2 unique channels to operate on.')
            self.path = Path(vert)
        else:
            if len(channels) != 1:
                raise Exception('You must define 1 unique channel to operate on.')

            if self.__class__ is isinstance(ThresholdGate) and len(vert) != 2:
                raise Exception('vert must be a single number (x_threshold)')
            elif self.__class__ is isinstance(IntervalGate) and len(vert) != 2:
                raise Exception('vert must be a single number (x_threshold)')
"""
import graph
from matplotlib.path import Path
from GoreUtilities.util import to_list
import pylab as pl
import numpy
from matplotlib import docstring
from common_doc import doc_replacer

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
    def __and__(self, other): return CompositeGate(self, 'and', other)
    def __xor__(self, other): return CompositeGate(self, 'xor', other)
    def __or__(self, other): return CompositeGate(self, 'or', other)
    def __invert__(self): return CompositeGate(self, 'invert')


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
        self.validiate_input()

    def validiate_input(self):
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
                raise ValueError('Trying to filter based on channel {channel}, which is not present in the data.'.format(channel=c))

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
                                but figure axis correspond to channels {1}""".format(c, ax_channels))
        if len(self.channels) == 2:
            c = self.channels[1]
            if c not in ax_channels:
                raise Exception("""Trying to plot gate that is defined on channel {0},
                                but figure axis correspond to channels {1}""".format(c, ax_channels))
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
            raise ValueError("region must be one of the following: {0}".format(self._region_options))

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
        idx = dataframe[self.channels[0]] >= self.vert # Get indexes that are above threshold

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

    def validiate_input(self):
        if self.vert[1] <= self.vert[0]:
            raise Exception('vert[1] must be larger than vert[0]')

    def _identify(self, dataframe):
        """ Identifies which data points in the dataframe pass the gate. """
        ##
        # Let's get the indecies that are within the interval
        idx1 = self.vert[0] <= dataframe[self.channels[0]]

        # Should this comparison use a filtered array (using idx1) for optimization? Check
        idx2 = dataframe[self.channels[0]] <= self.vert[1]

        idx = idx1 & idx2

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
        self.path = Path(vert)
        self._region_options = ('in', 'out')
        super(PolyGate, self).__init__(vert, channels, region, name)

    def _identify(self, dataframe):
        """
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe : DataFrame
        """
        idx = self.path.contains_points(dataframe.filter(self.channels))

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
    """
    def __init__(self, gate1, how, gate2=None):
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
            return '{0} {2} {1}'.format(*self.gates).format(self.how)

    def __str__(self):
        return self.__name__

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
            raise ValueError("Unsupported value for how. how must be in ({0})".format(supported_values))

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

if __name__ == '__main__':
    print Gate.__init__.__doc__
    print PolyGate.__init__.__doc__
    print QuadGate.__init__.__doc__
    print ThresholdGate.__init__.__doc__
    print IntervalGate.__init__.__doc__

    print PolyGate.plot.__doc__
    print QuadGate.plot.__doc__
    print ThresholdGate.plot.__doc__
    print IntervalGate.plot.__doc__
