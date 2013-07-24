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

def plotFCM(data, channel_names, transform=(None, None), kind='histogram', ax=None,
                autolabel=True, xlabel_kwargs={}, ylabel_kwargs={},
                **kwargs):
    '''
    Plots the sample on the current axis.
    Follow with a call to matplotlibs show() in order to see the plot.

    Parameters
    ----------
    FCMdata : fcm data object
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

    # Transform data
    #transformList = to_list(transform)


    if len(channel_names) == 1:
        # 1d so histogram plot
        kwargs.setdefault('color', 'gray')
        kwargs.setdefault('histtype', 'stepfilled')

        pHandle = data[channel_names[0]].hist(ax = ax, **kwargs)

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

def plot_gate(gate_type, coordinates, ax=None, gate_name=None, *args, **kwargs):
    '''
    Plots a gate on the current axis.

    TODO: Implement Interval Gate
    TODO: This function should not rescale (probably)

    Parameters
    ----------
    gate_type : 'quad', 'polygon', 'interval', 'threshold'
        specifies the shape of the gate
    coordinates : tuple
        For:
            'quad'     gate : a tuple of two numbers (x, y)
            'polygon'  gate : a tuple of 3 or more 2d coordinates ((x1, y1), (x2, y2), (x3, y3), ...)
            'interval' gate : a tuple of (channel_name, x1 or y1, x2 or y2) ?? Still need to specify channel names

    transform : tuple
        each element is set to None or 'logicle'
        if 'logicle' then channel data is transformed with logicle transformation

    gate_name : str | None
        Not supported yet

    Returns
    -------
    reference to plot
    '''
    if gate_type == 'quad':
        return plot_quad_gate(coordinates[0], coordinates[1], ax=ax, *args, **kwargs)
    elif gate_type == 'polygon':
        return plot_polygon_gate(coordinates, ax=ax, *args, **kwargs)

def plot_quad_gate(x, y, ax=None, *args, **kwargs):
    '''
    Plots a quad gate.
    vertical line at x
    horizontal line at y
    TODO: This function should not rescale (probably)
    '''
    if ax == None:
        ax = pl.gca()
    kwargs.setdefault('color', 'black')
    pl.axvline(x, *args, **kwargs)
    pl.axhline(y, *args, **kwargs)

def plot_polygon_gate(coordinateList, ax=None, *args, **kwargs):
    '''
    Plots a polygon gate on the current axis.
    (Just calls the polygon function)
    TODO: This function should not rescale (probably)

    Parameters
    ----------
    coordinates : a list of 3 or more 2-tuples
            i.e. [(x1, y1), (x2, y2), (x3, y3), ...]

    *args, **kwargs are passed to the Polygon function

    Returns
    -------
    Created artist
    '''
    if ax == None:
        ax = pl.gca()

    kwargs.setdefault('fill', False)
    kwargs.setdefault('color', 'black')
    poly = pl.Polygon(coordinateList, *args, **kwargs)
    return ax.add_artist(poly)

