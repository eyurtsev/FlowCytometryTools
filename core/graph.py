#!/usr/bin/env python
from fcm.graphics.util import bilinear_interpolate
from bases import to_list
import numpy
import matplotlib.pylab as plt

def plot_2dhistogram(x, y, bins=200, **kwargs):
    '''
    Plots a 2D histogram given x, y and number of bins
    '''
    # Estimate the 2D histogram
    H, xedges, yedges = numpy.histogram2d(x,y,bins=bins)
    # H needs to be rotated and flipped
    H = numpy.rot90(H)
    H = numpy.flipud(H)
    # Mask zeros
    Hmasked = numpy.ma.masked_where(H==0,H) # Mask pixels with a value of zero
    return plt.pcolormesh(xedges,yedges, Hmasked, **kwargs)

def pseudocolor_bilinear_interpolate(x, y, edgecolors='none', s=1, **kwargs):
    '''
    Pseudocolor plot based on FCMs bilinear interpolate function.
    '''
    z = bilinear_interpolate(x, y)
    return plt.scatter(x, y, c=z, s=s, edgecolors=edgecolors, **kwargs)

def plotFCM(data, channel_names, transform=(None, None), plot2d_type='dot2d', **kwargs):
    '''
    Plots the sample on the current axis.
    Follow with a call to matplotlibs show() in order to see the plot.

    Parameters
    ----------
    FCMdata : fcm data object
    channel_names : str| iterable of str | None
        name (names) channels to plot.
        given a single channel plots a histogram
        given two channels produces a 2d plot

    transform : tuple
        each element is set to None or 'logicle'
        if 'logicle' then channel data is transformed with logicle transformation

    plot2d_type : 'dot2d', 'hist2d', 'pseudo with bilinear'

    Returns
    -------
    pHandle: reference to plot
    '''
    # Find indexes of the channels
    channel_names = to_list(channel_names)
    channelIndexList = [data.name_to_index(channel) for channel in channel_names]

    # Transform data
    transformList = to_list(transform)

    for channel, transformType in zip(channelIndexList, transformList):
        if transformType == 'logicle':
            data.logicle(channels=[channel])

    if len(channelIndexList) == 1:
        # 1d so histogram plot
        ch1i = channelIndexList[0]
        pHandle = plt.hist(data[:, ch1i], **kwargs)

    elif len(channelIndexList) == 2:
        x = data[:, channelIndexList[0]] # index of first channels name
        y = data[:, channelIndexList[1]] # index of seconds channels name

        if plot2d_type == 'dot2d':
            pHandle = plt.scatter(x, y, **kwargs)
        elif plot2d_type == 'hist2d':
            pHandle = plot_2dhistogram(x, y, **kwargs)
        elif plot2d_type =='pseudo with bilinear':
            pHandle = pseudocolor_bilinear_interpolate(x, y, **kwargs)
        else:
            raise Exception('Not a valid plot type')

    return pHandle


