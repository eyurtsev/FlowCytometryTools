""""
@author: Eugene Yurtsev
@date 2013-07-25

Defines filters to be used for filter flow cytometry data.

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

class Gate(object):
    """ Abstract gate. Defines common interface for specific implementations of the gate classes. """
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
        pass

    def __repr__(self):
        return """Gate Type: {0}
               \tVertices: {1}
               \tChannel(s): {2}
               \tName: {3}
                """.format(self.__class__, self.vert, self.channels, self.name)

    def __str__(self):
        return self.__repr__()

    def __call__(self, dataframe, region = None):
        """
        TODO: Update documentation.
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame
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
                    flip=False
                else:
                    flip=True
            except ValueError:
                raise Exception, 'Trying to plot gate that is defined on channel %s, but figure axis correspond to channels %s' %(c, ax_channels)
        if len(self.channels) == 2:
            c = self.channels[1]
            if c not in ax_channels:
                raise Exception, 'Trying to plot gate that is defined on channel %s, but figure axis correspond to channels %s' %(c, ax_channels)
        return flip

    def plot(self, **kwargs):
        raise NotImplementedError('Plotting is not yet supported for this gate type.')

    def _identify(self, dataframe):
        raise NotImplementedError

    @property
    def region(self):
        """ Defines the region of the gate that is used for filtering. """
        return self._region

    @region.setter
    def region(self, value):
        if value.lower() in self._region_options:
            self._region = value.lower()
        else:
            raise ValueError("region must be one of the following: {0}".format(self._region_options))



class ThresholdGate(Gate):
    def __init__(self, threshold, channel, region, name=None):
        """
        Parameters
        ----------
        threshold : a float

        channel : 'str'
            Defines the channel name

        name : 'str'
            Specifies the name of the gate.
        """
        self._region_options = ('above', 'below')

        super(ThresholdGate, self).__init__(threshold, channel, region, name)

    def _identify(self, dataframe):
        """ Identifies which of the data points in the dataframe pass the gate. """
        idx = dataframe[self.channels[0]] >= self.vert # Get indexes that are above threshold

        if self.region == 'below':
            idx = ~idx

        return idx

    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        Plots a threshold gate.
        TODO: This function should not rescale the axis
        Warning: The plot function does not check that your
        axis correspond to the correct channels.

        Parameters
        ----------
        ax : axes to use for plotting the gate on
        flip : boolean
            If true assumes draws the interval
            along the y-axis instead of along the x-axis

        Returns
        -------
        Reference to created artists.
        """
        if ax == None:
            ax = pl.gca()

        if ax_channels is not None:
            flip = self._find_orientation(ax_channels)
        
        plot_func = ax.axes.axhline if flip else ax.axes.axvline
        
        kwargs.setdefault('color', 'black')
        return plot_func(self.vert, *args, **kwargs)


class IntervalGate(Gate):
    def __init__(self, vert, channel, region, name=None):
        """
        Parameters
        ----------
        vert : a 2-tuple (x_min, x_max)

        channels : 'str'
            Defines the channel name

        name : 'str'
            Specifies the name of the gate.
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


    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        Plots an interval gate
        TODO: This function should not rescale the axis
        Warning: The plot function does not check that your
        axis correspond to the correct channels.

        Parameters
        ----------
        ax : axes to use for plotting the gate on
        flip : boolean
            If true assumes draws the interval
            along the y-axis instead of along the x-axis

        Returns
        -------
        Reference to created artists.
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
    def __init__(self, vert, channels, region, name=None):
        """
        Parameters
        ----------
        vert : a 2-tuple (x_center, y_center)

        channels : ['channel 1 name', 'channel 2 name']
            Defines the names of the channels

        name : 'str'
            Specifies the name of the gate.
        """
        self._region_options = ('top left', 'top right', 'bottom left', 'bottom right')
        super(QuadGate, self).__init__(vert, channels, region, name)

    def _identify(self, dataframe):
        """
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        region : 'top left' | 'top right' | 'bottom left' | 'bottom right'
            The first channel passed to the gate constructor is assumed to be the x-axis.
            The second channel is the y-axis.
            Add optional 'out' to have the cells that are outside of the specified region.

        # TODO Fix this implementation. (i.e., why not support just 'left')
        # At the moment this implementation won't work at all.
        The logic here can be simplified.
        """
        id1 = dataframe[self.channels[0]] >= self.vert[0]
        id2 = dataframe[self.channels[1]] >= self.vert[1]

        if 'left' in self.region: id1 = ~id1
        if 'bottom' in self.region: id2 = ~id2

        idx = id1 & id2

        if 'out' in self.region:
            idx = ~idx

        return idx


    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        Plots a quad gate.
        TODO: This function should not rescale the axis
        Warning: The plot function does not check that your x and y axis correspond to the
        correct channels

        Parameters
        ----------
        ax - axes to use for plotting the gate on

        Returns
        -------
        Reference to created artists. (2-tuple)
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
    def __init__(self, vert, channels, region='in', name=None):
        """
        Parameters
        ----------
        vert : a list of 2-tuples [(x1, y1), (x2, y2), (x3, y3)]

        channels : ['channel 1 name', 'channel 2 name']
            Defines the names of the channels

        name : 'str'
            Specifies the name of the gate.
        """
        self.path = Path(vert)
        self._region_options = ('in', 'out')
        super(PolyGate, self).__init__(vert, channels, region, name)

    def _identify(self, dataframe):
        """
        Returns a list of indexes containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        region : 'in' | 'out'
            Determines whether to return the points
            inside ('in') or outside ('out') of the polygon
        """
        idx = self.path.contains_points(dataframe.filter(self.channels))

        if self.region == 'out':
            idx = ~idx

        return idx

    def plot(self, flip=False, ax_channels=None, ax=None, *args, **kwargs):
        """
        Plots a polygon gate on the current axis.
        (Just calls the polygon function)
        TODO: This function should not rescale the axis

        Parameters
        ----------
        ax - axes to use for plotting the gate on

        Returns
        -------
        Reference to created artist
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


def filter(data, gate_list, how='all'):
    """
    """
    idx = [gate._identify(data) for gate in gate_list]

    if how == 'all':
        function = numpy.all
    elif how == 'any':
        function = numpy.any
    else:
        raise ValueError("how must be 'all' or 'any'")

    idx = function(idx, axis=0)

    return data[idx]



if __name__ == '__main__':
    pass
