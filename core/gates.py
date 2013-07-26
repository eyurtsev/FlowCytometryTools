""""
@author: Eugene Yurtsev
@date 2013-07-25

Defines filters to be used for filter flow cytometry data.

API:
    DataFrame -- pandas object
    gate1 -- a polygon gate.

gate = PolygonGate(ID='Hello', coordinates=())

DataFrame = gate.filter(DataFrame)

DataFrame = gate.filter(DataFrame, which='in') # Inside the gate
DataFrame = gate.filter(DataFrame, which='out') # Outside the gate

DataFrame = gate.filter(DataFrame, which='above') # Outside the gate
DataFrame = gate.filter(DataFrame, which='below') # Outside the gate

DataFrame = gate.filter(DataFrame, which='top left') # Outside the gate
"""
import graph
from matplotlib.path import Path
from GoreUtilities.util import to_list

class Gate(object):
    """ Abstract gate. Defines common interface for specific implementations of the gate classes. """
    def __init__(self, vert, channels, name=None):
        self.vert = vert
        channels = to_list(channels)
        self.channels = channels
        self.name = "Unnamed Gate" if name is None else name

        """ Should we be checking inputs here? Perhaps split to different __init__ methods so that
        each one can have it's own documentation. That will probably be clearer to the user anyway.
        """


        self.validiate_input()

        #if self.__class__ is isinstance(PolyGate):
            #if len(vert) < 2:
                #raise Exception('vert must be a list of 2-tuples [(x1, y1), (x2, y2), (x3, y3)]')
            #if len(channels) != 2 or channel[0] == channel[1]:
                #raise Exception('You must define 2 unique channels to operate on.')
            #self.path = Path(vert)
        #else:
            #if len(channels) != 1:
                #raise Exception('You must define 1 unique channel to operate on.')
#
            #if self.__class__ is isinstance(ThresholdGate) and len(vert) != 2:
                #raise Exception('vert must be a single number (x_threshold)')
            #elif self.__class__ is isinstance(IntervalGate) and len(vert) != 2:
                #raise Exception('vert must be a single number (x_threshold)')


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

    def filter(self):
        raise Exception('Not implemented')

    def plot(self, ax=None, *args, **kwargs):
        """
        Plots a gate object on the current axis.
        Note: this function may or may not rescale the x,y axis

        TODO: Does not work for Interval Gate

        Parameters
        ----------
        ax : axis reference to plot on

        *args, **kwargs
            + passed to the Polygon function for the polygon gate
            + passed to axvline and axhline for quad gate

        Returns
        -------
        reference to plot
        """
        if isinstance(self, PolyGate):
            gate_type = 'polygon'
        elif isinstance(self, QuadGate):
            gate_type = 'quad'
        else:
            raise Exception('Plotting is not yet supported for this gate type.')

        graph.plot_gate(gate_type, self.vert, ax=ax, *args, **kwargs)

class ThresholdGate(Gate):
    def __init__(self, threshold, channel=None, name=None):
        """
        Parameters
        ----------
        threshold : a float

        channel : 'str'
            Defines the channel name

        name : 'str'
            Specifies the name of the gate.
        """
        super(ThresholdGate, self).__init__(threshold, channel, name)

    def filter(self, dataframe, which):
        """
        Returns a filtered data frame containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        which : 'above' | 'below'
            Determines whether to return the points
            that are above or else below the threshold.
        """
        idx = dataframe[self.channels[0]] >= self.vert

        if which == 'above':
            return dataframe[idx]
        elif which == 'below':
            return dataframe[~idx]
        else:
            raise Exception("""Unrecognized option for which must be 'above' or 'below'.""")

class IntervalGate(Gate):
    def __init__(self, vert, channel, name=None):
        """
        Parameters
        ----------
        vert : a 2-tuple (x_min, x_max)

        channels : 'str'
            Defines the channel name

        name : 'str'
            Specifies the name of the gate.
        """
        super(IntervalGate, self).__init__(vert, channel, name)

    def validiate_input(self):
        if self.vert[1] <= self.vert[0]:
            raise Exception('vert[1] must be larger than vert[0]')

    def filter(self, dataframe, which='in'):
        """
        Returns a filtered data frame containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        which : 'in' | 'out'
            Determines whether to return the points
            are inside or else outside the interval.

        """
        # This is not optimized. The second comparison should be on the filtered array.
        idx1 = self.vert[0] <= dataframe[self.channels[0]]
        idx2 = dataframe[self.channels[0]] <= self.vert[1]

        idx = idx1 & idx2

        if which == 'in':
            return dataframe[idx]
        elif which == 'out':
            return dataframe[~idx]
        else:
            raise Exception("""Unrecognized option for which must be 'in' or 'out'.""")

class QuadGate(Gate):
    def __init__(self, vert, channels, name=None):
        """
        Parameters
        ----------
        vert : a 2-tuple (x_center, y_center)

        channels : ['channel 1 name', 'channel 2 name']
            Defines the names of the channels

        name : 'str'
            Specifies the name of the gate.
        """
        super(QuadGate, self).__init__(vert, channels, name)

    def filter(self, dataframe, which):
        """
        Returns a filtered data frame containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        which : 'top left' | 'top right' | 'bottom left' | 'bottom right'
            The first channel passed to the gate constructor is assumed to be the x-axis.
            The second channel is the y-axis.
            Add optional 'out' to have the cells that are outside of the specified region.

        # TODO Fix this implementation. (i.e., why not support just 'left')
        The logic here can be simplified.
        """
        id1 = dataframe[self.channels[0]] >= self.vert[0]
        id2 = dataframe[self.channels[1]] >= self.vert[1]

        which = which.strip().lower()

        if 'left' not in which and 'right' not in which:
            raise Exception('Please select a valid option for which')

        if 'top' not in which and 'bottom' not in which:
            raise Exception('Please select a valid option for which')

        if 'left' in which: id1 = ~id1

        if 'bottom' in which: id2 = ~id2

        idx = id1 & id2

        if 'out' in which:
            idx = ~idx

        return dataframe[idx]

class PolyGate(Gate):
    def __init__(self, vert, channels, name=None):
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

        super(PolyGate, self).__init__(vert, channels, name)

    def filter(self, dataframe, which='in'):
        """
        Returns a filtered data frame containing only the points that pass the filter.

        Parameters
        ----------
        dataframe: DataFrame

        which : 'in' | 'out'
            Determines whether to return the points
            inside ('in') or outside ('out') of the polygon
        """
        idx = self.path.contains_points(dataframe[self.channels])
        if which == 'in':
            return dataframe[idx]
        elif which == 'out':
            return dataframe[~idx]
        else:
            raise Exception("""Unrecognized option for which must be 'in' or 'out'.""")


if __name__ == '__main__':
    pass
