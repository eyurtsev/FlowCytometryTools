#!/usr/bin/env python
"""
Modules contains graphing routines common for flow cytometry files.
"""
from GoreUtilities.util import to_list
import numpy
import pylab as pl
import matplotlib

def plot_histogram2d(x, y, bins=200, ax=None, **kwargs):
    '''
    Plots a 2D histogram given x, y and number of bins

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
    kwargs : kwargs
        passed to pcolormesh

    Plotting Defaults
    -----------------
        kwargs.setdefault('cmap', pl.cm.copper)
        kwargs.setdefault('norm', matplotlib.colors.LogNorm())

    Returns
    -------
    Reference to plot
    '''
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
    return ax.pcolormesh(xedges, yedges, masked_hist, **kwargs)

def plotFCM(data, channel_names, kind='histogram', ax=None,
                autolabel=True, xlabel_kwargs={}, ylabel_kwargs={},
                **kwargs):
    '''
    Plots the sample on the current axis.
    Follow with a call to matplotlibs show() in order to see the plot.

    Parameters
    ----------
    data : DataFrame
    channel_names : str| iterable of str
        name (names) channels to plot.
        given a single channel plots a histogram
        given two channels produces a 2d plot

    transform : tuple
        each element is set to None or 'logicle'
        if 'logicle' then channel data is transformed with logicle transformation

    kind : 'scatter' | 'histogram'
        Specifies the kind of plot to use for plotting the data (only applies to 2D plots).

    autolabel : False | True
        If True the x and y axes are labeled automatically.

    ax : reference | None
        specifies which axis to plot on

    Returns
    -------
    pHandle: reference to plot
    '''
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
            pHandle = x.hist(ax = ax, **kwargs)
        else:
            return None

    elif len(channel_names) == 2:
        x = data[channel_names[0]] # index of first channels name
        y = data[channel_names[1]] # index of first channels name

        if kind == 'scatter':
            kwargs.setdefault('edgecolor', 'none')
            pHandle = ax.scatter(x, y, **kwargs)
        elif kind == 'histogram':
            pHandle = plot_histogram2d(x, y, ax=ax, **kwargs)
        else:
            raise Exception("Not a valid plot type. Must be 'scatter', 'histogram'")

    if autolabel:
        y_label_text = 'Counts' if len(channel_names) == 1 else channel_names[1]
        ax.set_xlabel(channel_names[0], **xlabel_kwargs)
        ax.set_ylabel(y_label_text, **ylabel_kwargs)

    return pHandle
