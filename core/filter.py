""""
Redefines fcm gates to include plotting capability
"""

import fcm
import graph

class PlottableFilter(object):
    def plot(self, ax=None, *args, **kwargs):
        '''
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
        '''
        if isinstance(self, PolyGate):
            gate_type = 'polygon'
        elif isinstance(self, QuadGate):
            gate_type = 'quad'

        graph.plot_gate(gate_type, self.vert, ax=ax, *args, **kwargs)


class PolyGate(PlottableFilter, fcm.PolyGate):
    pass

class QuadGate(PlottableFilter, fcm.QuadGate):
    pass

