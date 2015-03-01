#!/usr/bin/env python
"""
Modules contains graphing routines common for flow cytometry files.
"""
from GoreUtilities.util import to_list
import numpy
import pylab as pl
import matplotlib
from common_doc import doc_replacer
import warnings

@doc_replacer
def plotFCM(data, channel_names, kind='histogram', ax=None,
                autolabel=True, xlabel_kwargs={}, ylabel_kwargs={},
                colorbar=False, grid=False,
                **kwargs):
    """
    Plots the sample on the current axis.

    Follow with a call to matplotlibs show() in order to see the plot.

    Parameters
    ----------
    data : DataFrame
    {graph_plotFCM_pars}
    {common_plot_ax}

    Returns
    -------
    The output of the plot command used
    """
    if ax == None: ax = pl.gca()

    xlabel_kwargs.setdefault('size', 16)
    ylabel_kwargs.setdefault('size', 16)

    channel_names = to_list(channel_names)

    if len(channel_names) == 1:
        # 1D so histogram plot
        kwargs.setdefault('color', 'gray')
        kwargs.setdefault('histtype', 'stepfilled')
        kwargs.setdefault('bins', 200) # Do not move above

        x = data[channel_names[0]].values
        if len(x) >= 1:
            if (len(x) == 1) and isinstance(kwargs['bins'], int):
                # Only needed for hist (not hist2d) due to hist function doing
                # excessive input checking
                warnings.warn("One of the data sets only has a single event. "\
                        "This event won't be plotted unless the bin locations"\
                        " are explicitely provided to the plotting function. ")
                return None
            plot_output = ax.hist(x, **kwargs)
        else:
            return None

    elif len(channel_names) == 2:
        x = data[channel_names[0]].values # value of first channel
        y = data[channel_names[1]].values # value of second channel

        if len(x) == 0:
            # Don't draw a plot if there's no data
            return None
        if kind == 'scatter':
            kwargs.setdefault('edgecolor', 'none')
            plot_output = ax.scatter(x, y, **kwargs)
        elif kind == 'histogram':
            kwargs.setdefault('bins', 200) # Do not move above
            kwargs.setdefault('cmin', 1)
            kwargs.setdefault('cmap', pl.cm.copper)
            kwargs.setdefault('norm', matplotlib.colors.LogNorm())
            plot_output = ax.hist2d(x, y, **kwargs)
            mappable = plot_output[-1]

            if colorbar:
                pl.colorbar(mappable, ax=ax)
        else:
            raise ValueError("Not a valid plot type. Must be 'scatter', 'histogram'")

    pl.grid(grid)

    if autolabel:
        y_label_text = 'Counts' if len(channel_names) == 1 else channel_names[1]
        ax.set_xlabel(channel_names[0], **xlabel_kwargs)
        ax.set_ylabel(y_label_text, **ylabel_kwargs)

    return plot_output

if __name__ == '__main__':
    #print docstring.interpd.params.keys()
    #print plot_histogram2d.__doc__
    print plotFCM.__doc__
