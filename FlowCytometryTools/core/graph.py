#!/usr/bin/env python
"""
Modules contains graphing routines common for flow cytometry files.
"""
from GoreUtilities.util import to_list
import numpy
import pylab as pl
import matplotlib
from common_doc import doc_replacer

def plot_histogram2d(x, y, bins=200, ax=None, colorbar=True, **kwargs):
    """
    Plots a 2D histogram given x, y and number of bins.

    Parameters
    ----------
    x : array
        array of x coordinates
    y : array
        array of y coordinates
    bins : int
        number of bins to break the data into
    ax : reference to axis
        axis to plot on
    kwargs : key word arguments
        passed to pcolormesh

    Plotting Defaults
    -----------------

    kwargs.setdefault('cmap', pl.cm.copper)
    kwargs.setdefault('norm', matplotlib.colors.LogNorm())

    Returns
    -------
    output of pcolormesh
    """
    if ax == None:
        ax = pl.gca()

    kwargs.setdefault('cmap', pl.cm.copper)
    kwargs.setdefault('norm', matplotlib.colors.LogNorm())

    # Estimate the 2D histogram
    counts_hist, xedges, yedges = numpy.histogram2d(x, y, bins=bins)
    # counts_hist needs to be rotated and flipped
    counts_hist = numpy.rot90(counts_hist)
    counts_hist = numpy.flipud(counts_hist)
    # Mask zeros with a value of 0
    masked_hist = numpy.ma.masked_where(counts_hist == 0, counts_hist)


    p = ax.pcolormesh(xedges, yedges, masked_hist, **kwargs)
    if colorbar:
        pl.colorbar(p)
    return p


@doc_replacer
def plotFCM(data, channel_names, kind='histogram', ax=None,
                autolabel=True, xlabel_kwargs={}, ylabel_kwargs={},
                colorbar=False,
                **kwargs):
    """
    Plots the sample on the current axis.

    Follow with a call to matplotlibs show() in order to see the plot.

    Parameters
    ----------
    data : DataFrame
    {graph_plotFCM_pars}

    Returns
    -------
    The output of the plot command used
    """
    if ax == None: ax = pl.gca()

    xlabel_kwargs.setdefault('size', 16)
    ylabel_kwargs.setdefault('size', 16)

    channel_names = to_list(channel_names)

    if len(channel_names) == 1:
        # 1d so histogram plot
        kwargs.setdefault('color', 'gray')
        kwargs.setdefault('histtype', 'stepfilled')

        x = data[channel_names[0]]
        if len(x):
            plot_output = ax.hist(x, **kwargs)
        else:
            return None

    elif len(channel_names) == 2:
        x = data[channel_names[0]] # index of first channels name
        y = data[channel_names[1]] # index of first channels name

        if kind == 'scatter':
            kwargs.setdefault('edgecolor', 'none')
            plot_output = ax.scatter(x, y, **kwargs)
        elif kind == 'histogram':
            plot_output = plot_histogram2d(x, y, ax=ax, colorbar=colorbar, **kwargs)
        else:
            raise Exception("Not a valid plot type. Must be 'scatter', 'histogram'")

    if autolabel:
        y_label_text = 'Counts' if len(channel_names) == 1 else channel_names[1]
        ax.set_xlabel(channel_names[0], **xlabel_kwargs)
        ax.set_ylabel(y_label_text, **ylabel_kwargs)

    return plot_output

if __name__ == '__main__':
    #print docstring.interpd.params.keys()
    #print plot_histogram2d.__doc__
    print plotFCM.__doc__
