#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2013 Eugene Yurtsev and Jonathan Friedman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function

import os
import re
import time

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy
import numpy as np
import pandas
import pylab as pl
from matplotlib import transforms
from numpy import arange, linspace

from FlowCytometryTools.utility_lib import docstring
from FlowCytometryTools.utility_lib import util

###############################
#### PLOTTING TO SUBPLOTS #####
###############################

_doc_dict = dict(
    _graph_grid_layout="""\
xlim : None | 2-tuple
    If None automatic, otherwise specifies the xmin and xmax for the plot
ylim : None | 2-tuple
    If None automatic, otherwise specifies the ymin and ymax for the plot
row_label_xoffset : float
    Additional offset for the row labels in the x direction.
col_label_yoffset : float
    Additional offset for the col labels in the y direction.
hide_tick_labels : True | False
    Hides the tick mark labels.
hide_tick_lines : True | False
    Hides the tick marks.
hspace : float
    Horizontal space between subplots.
wspace : float
    Vertical space between subplots.
row_labels_kwargs : dict
    This dict is unpacked into the pylab.text function
    that draws the row labels.
col_labels_kwargs : dict
    This dict is unpacked into the pylab.text function
    that draws the column labels.""",

    _graph_grid_layout_returns="""\
(ax_main, ax_subplots)
    ax_main : reference to the main axes
    ax_subplots : matrix of references to the subplots (e.g., ax_subplots[0, 3] references
    the subplot in row 0 and column 3.)"""
)

doc_replacer = docstring.DocReplacer(**_doc_dict)


@doc_replacer
def create_grid_layout(rowNum=8, colNum=12, row_labels=None, col_labels=None,
                       xlim=None, ylim=None,
                       xlabel=None, ylabel=None,
                       row_label_xoffset=None, col_label_yoffset=None,
                       hide_tick_labels=True, hide_tick_lines=False,
                       hspace=0, wspace=0,
                       row_labels_kwargs={},
                       col_labels_kwargs={},
                       subplot_kw={},
                       xscale=None, yscale=None,
                       plotFuncList=None):
    """
    Creates a figure with a 2d matrix of subplots (rows=rowNum, cols=colNum), automatically annotating
    and setting default plotting settings for the subplots.

    The function creates a main axes that is invisible but
    can be used for setting x and y labels.
    On top of the main axes, it creates the subplots, which are used for plotting.

    Parameters
    ----------
    rowNum : int
        Specifies the number of rows
    colNum : int
        Specifies the number of columns
    row_labels : [list of str, None]
        Used for labeling each row of subplots
        If set to None, no labels are written. Default is None.
    col_labels : [list of str, None]
        Used for labeling each col of subplots.
        If set to None, no labels are written. Default is None.
    {_graph_grid_layout}
    plotFuncList : list of callable functions
        Each function must accept row, col arguments
        Each of these functions must know how to plot using the row, col arguments

    Returns
    -------
    {_graph_grid_layout_returns}

    How to use
    ----------
    Call this function with the desired parameters.
    Use the references to the individual subplot axis to plot.

    Call autoscale() command after plotting on the subplots in order to adjust their limits properly.
    """

    fig = plt.gcf()  # get reference to current open figure

    # Configure main axis appearance
    ax_main = plt.gca()

    # Hides the main axis but retains the ability to use xlabel, ylabel
    for spine in ax_main.spines.values():
        spine.set_visible(False)
    ax_main.patch.set_alpha(0)
    # ax_main.axison = False # If true, xlabel and ylabel do not work

    set_tick_lines_visibility(ax_main, False)
    set_tick_labels_visibility(ax_main, False)

    # Configure subplot appearance
    subplot_kw.update(xlim=xlim, ylim=ylim, xscale=xscale,
                      yscale=yscale)  # This could potentially confuse a user

    plt.subplots_adjust(wspace=wspace, hspace=hspace)
    _, ax_subplots = plt.subplots(rowNum, colNum, squeeze=False,
                                  subplot_kw=subplot_kw, num=fig.number)

    # configure defaults for appearance of row and col labels
    row_labels_kwargs.setdefault('horizontalalignment', 'right')
    row_labels_kwargs.setdefault('verticalalignment', 'center')
    row_labels_kwargs.setdefault('size', 'x-large')

    col_labels_kwargs.setdefault('horizontalalignment', 'center')
    col_labels_kwargs.setdefault('verticalalignment', 'top')
    col_labels_kwargs.setdefault('size', 'x-large')

    # Translate using figure coordinates

    row_label_translation = -0.10

    if row_label_xoffset:
        row_label_translation -= row_label_xoffset

    col_label_translation = -0.10

    if col_label_yoffset:
        col_label_translation -= col_label_yoffset

    offset_row_labels = transforms.ScaledTranslation(row_label_translation, 0, fig.dpi_scale_trans)
    offset_col_labels = transforms.ScaledTranslation(0, col_label_translation, fig.dpi_scale_trans)

    for (row, col), ax in numpy.ndenumerate(ax_subplots):
        plt.sca(ax)  # Sets the current axis for all plotting operations

        if row_labels is not None and col == 0:
            plt.text(0, 0.5, '{0}'.format(row_labels[row]),
                     transform=(ax.transAxes + offset_row_labels), **row_labels_kwargs)
            # plt.text(0 + row_label_translation, 0.5, '{0}'.format(row_labels[row]), transform=(ax.transAxes), **row_labels_kwargs)

        if col_labels is not None and row == (rowNum - 1):
            plt.text(0.5, 0, '{0}'.format(col_labels[col]),
                     transform=(ax.transAxes + offset_col_labels), **col_labels_kwargs)
            # plt.text(0.5, 0+ col_label_translation, '{0}'.format(col_labels[col]), transform=(ax.transAxes), **col_labels_kwargs)

        if row == 0 and col == colNum - 1:
            visible = [False, False]

            if xlabel:
                ax.xaxis.tick_top()
                ax.xaxis.set_label_position('top')
                ax.set_xlabel(xlabel, fontsize='large', labelpad=5)
                visible[0] = True

            if ylabel:
                ax.yaxis.tick_right()
                ax.yaxis.set_label_position('right')
                ax.set_ylabel(ylabel, fontsize='large', labelpad=5)
                visible[1] = True

            set_tick_lines_visibility(ax, visible)
            set_tick_labels_visibility(ax, visible)
        else:
            if hide_tick_lines:
                set_tick_lines_visibility(ax, False)
            if hide_tick_labels:
                set_tick_labels_visibility(ax, False)

        if plotFuncList is not None:
            for plot_function in plotFuncList:
                plot_function(row, col)

    plt.sca(
        ax_main)  # Make sure this is right before the return statement. It is here to comply with a user's expectation to calls that make reference to gca().

    return (ax_main, ax_subplots)


def autoscale_subplots(subplots=None, axis='both'):
    """
    Sets the x and y axis limits for each subplot to match the x and y axis
    limits of the most extreme data points encountered.

    The limits are set to the same values for all subplots.

    Parameters
    -----------
    subplots : ndarray or list of matplotlib.axes.Axes

    axis : ['x' | 'y' | 'both' / 'xy' / 'yx' | 'none' / '']
        'x' : autoscales the x axis
        'y' : autoscales the y axis
        'both', 'xy', 'yx' : autoscales both axis
        'none', '' : autoscales nothing

    Returns
    -------------
    None
    """
    axis_options = ('x', 'y', 'both', 'none', '', 'xy', 'yx')
    if axis.lower() not in axis_options:
        raise ValueError('axis must be in {0}'.format(axis_options))

    if subplots is None:
        subplots = plt.gcf().axes

    data_limits = [(ax.xaxis.get_data_interval(), ax.yaxis.get_data_interval()) for loc, ax in
                   numpy.ndenumerate(subplots)]  # TODO: Make a proper iterator
    xlims, ylims = zip(*data_limits)

    xmins_list, xmaxs_list = zip(*xlims)
    ymins_list, ymaxs_list = zip(*ylims)

    xmin = numpy.min(xmins_list)
    xmax = numpy.max(xmaxs_list)

    ymin = numpy.min(ymins_list)
    ymax = numpy.max(ymaxs_list)

    for loc, ax in numpy.ndenumerate(subplots):
        if axis in ('x', 'both', 'xy', 'yx'):
            ax.set_xlim((xmin, xmax))
        if axis in ('y', 'both', 'xy', 'yx'):
            ax.set_ylim((ymin, ymax))


def scale_subplots(subplots=None, xlim='auto', ylim='auto'):
    """
    Sets the x and y axis limits for a collection of subplots.

    Parameters
    -----------
    subplots : ndarray or list of matplotlib.axes.Axes

    xlim : None | 'auto' | (xmin, xmax)
        'auto' : sets the limits according to the most
        extreme values of data encountered.
    ylim : None | 'auto' | (ymin, ymax)

    Returns
    -------------
    None
    """
    auto_axis = ''
    if xlim == 'auto':
        auto_axis += 'x'
    if ylim == 'auto':
        auto_axis += 'y'

    autoscale_subplots(subplots, auto_axis)

    for loc, ax in numpy.ndenumerate(subplots):
        if 'x' not in auto_axis:
            ax.set_xlim(xlim)
        if 'y' not in auto_axis:
            ax.set_ylim(ylim)


@doc_replacer
def plot_ndpanel(panel, func=None,
                 xlim='auto', ylim='auto',
                 row_labels='auto', col_labels='auto',
                 row_name='auto', col_name='auto',
                 pass_slicing_meta_to_func=False,
                 subplot_xlabel=None, subplot_ylabel=None,
                 row_name_pad=40.0, col_name_pad=40.0,
                 hspace=0, wspace=0,
                 hide_tick_labels=True, hide_tick_lines=False,
                 legend=None, legend_title=None,
                 grid_kwargs={},
                 **kwargs):
    """
    Use to visualize mutli-dimensional data stored in N-dimensional pandas panels.

    Given an nd-panel of shape (.., .., .., rows, cols), the function creates a 2d grid of subplot
    of shape (rows, cols). subplot i, j calls func parameter with an (n-2) nd panel that corresponds to (..., .., .., i, j).

    Parameters
    ---------------
    panel : pandas Panel (3d-5d.. indexing is hard coded at the moment)
        items : time series generated along this axis
        major : rows
        minor : cols
    func : function that accepts a slice of a panel (two dimensions less than input panel)
    {_graph_grid_layout}

    pass_slicing_meta_to_func : [False | True]
        Changes the arguments that are passed to the provided function.
        If False: func(data_slice, **kwargs) (Default)
        If True: func(data_slice, row=row, col=col, row_value=row_value, col_value=col_value, **kwargs)

    grid_kwargs : dict
        kwargs to be passed to the create_grid_layout method. See its documentation for further details.
    legend : None, tuple
        If provided as tuple, must be a 2-d tuple corresponding to a subplot position.
        If legend=(2, 4), then the legend will drawn using the labels of the lines provided in subplot in 2nd row and 4th column.
        A better name could be subplot_source_for_legend?
    legend_title : str, None
        If provided, used as title for the legend.

    Returns
    ---------------

    Reference to main axis and to subplot axes.

    Examples
    ----------------

    if a is a panel:

    plot_panel(a, func=plot, marker='o');

    Code that could be useful
    ---------------------------

    # Checks number of arguments function accepts
    if func.func_code.co_argcount == 1:
        func(data)
    else:
        func(data, ax)

    """
    auto_col_name, auto_col_labels, auto_row_name, auto_row_labels = extract_annotation(panel)
    shape = panel.values.shape
    rowNum, colNum = shape[-2], shape[-1]  # Last two are used for setting up the size
    ndim = len(shape)

    if ndim < 2 or ndim > 5:
        raise Exception('Only dimensions between 2 and 5 are supported')

    if row_labels == 'auto':
        row_labels = auto_row_labels
    if col_labels == 'auto':
        col_labels = auto_col_labels

    # Figure out xlimits and y limits
    axis = ''  # used below to autoscale subplots

    if xlim == 'auto':
        xlim = None
        axis += 'x'
    if ylim == 'auto':
        ylim = None
        axis += 'y'

    ax_main, ax_subplots = create_grid_layout(rowNum=rowNum, colNum=colNum,
                                              row_labels=row_labels, col_labels=col_labels,
                                              xlabel=subplot_xlabel, ylabel=subplot_ylabel,
                                              hide_tick_labels=hide_tick_labels,
                                              hide_tick_lines=hide_tick_lines,
                                              xlim=xlim, ylim=ylim, hspace=hspace, wspace=wspace,
                                              **grid_kwargs)

    nrange = arange(ndim)
    nrange = list(nrange[(nrange - 2) % ndim])  # Moves the last two dimensions to the first two

    if not isinstance(panel, pandas.DataFrame):
        panel = panel.transpose(*nrange)

    for (row, col), ax in numpy.ndenumerate(ax_subplots):
        plt.sca(ax)

        data_slice = panel.iloc[row].iloc[col]
        row_value = panel.axes[0][row]
        col_value = panel.axes[1][col]

        if pass_slicing_meta_to_func:
            func(data_slice, row=row, col=col, row_value=row_value, col_value=col_value, **kwargs)
        else:
            func(data_slice, **kwargs)

    autoscale_subplots(ax_subplots, axis)

    plt.sca(ax_main)

    if legend is not None:
        items, labels = ax_subplots[legend].get_legend_handles_labels()

        # lines = ax_subplots[legend].lines
        # l = pl.legend(lines , map(lambda x : x.get_label(), lines),
        l = pl.legend(items, labels,
                      bbox_to_anchor=(0.9, 0.5), bbox_transform=pl.gcf().transFigure,
                      loc='center left',
                      numpoints=1, frameon=False)
        if legend_title is not None:
            l.set_title(legend_title)

    if row_name == 'auto':
        row_name = auto_row_name
    if col_name == 'auto':
        col_name = auto_col_name
    if row_name is not None:
        pl.xlabel(col_name, labelpad=col_name_pad)
    if col_name is not None:
        pl.ylabel(row_name, labelpad=row_name_pad)

    #####
    # Placing ticks on the top left subplot
    ax_label = ax_subplots[0, -1]
    pl.sca(ax_label)

    if subplot_xlabel:
        xticks = numpy.array(pl.xticks()[0], dtype=object)
        xticks[1::2] = ''
        ax_label.set_xticklabels(xticks, rotation=90, size='small')

    if subplot_ylabel:
        yticks = numpy.array(pl.yticks()[0], dtype=object)
        yticks[1::2] = ''
        ax_label.set_yticklabels(yticks, rotation=0, size='small')

    pl.sca(ax_main)

    return ax_main, ax_subplots


def plot_ndpanel_1d(data, plot_func=None, ylabel=None, axes_num=0, ax_list=None,
                    autoscale_axis='both',
                    title='full', legend_subplot=0, legend_title=None, **kwargs):
    """Cycle through a requested dimension of an ndpanel and plots the result.

    Parameters
    ------------
    data : DataFrame | Panel | Panel4D | PanelND
    plot_func : callable | None
        The following information is passed to the plotting function:  (data.iloc[index], index, value, ax, **kwargs)
    ylabel : str
    axes_num : int | (implement str)
    ax_list : list of ax | None
        list of axes
    title : 'full' | 'value' | None

    Example
    ----------
    ax_list = subplots(2, 5, figsize=(14, 14))[1].flatten()
    subplots_adjust(wspace=0.4, hspace=0.4)
    plot_ndpanel_1d(data, ylabel='OD (600 nm)', title='value', ax_list=ax_list, legend_title='legend title')
    """
    num_dim = len(data.axes[axes_num])
    axes_name = data.axes[axes_num].name

    if ax_list is None:
        ax_list = [plt.subplot(num_dim, 1, i + 1) for i in range(num_dim)]

    def default_func(data, i, value, ax, **kwargs):
        kwargs.setdefault('legend', False)
        kwargs.setdefault('cmap', cm.coolwarm)
        cmap = kwargs.pop('cmap')
        color_set = cmap(linspace(0, 1, len(data.axes[1])))
        data.plot(ax=ax, color=color_set, **kwargs)

    if plot_func is None:
        plot_func = default_func

    for i, v in enumerate(data.axes[axes_num]):
        ax = ax_list[i]
        plot_func(data.iloc[i], i, v, ax, **kwargs)

        if title == 'full':
            title_str = '{} : {}'.format(axes_name, v)
        elif title == 'value':
            title_str = '{}'.format(v)
        if title is not None:
            ax.set_title(title_str)

        if ylabel is not None:
            ax.set_ylabel(ylabel)
    autoscale_subplots(ax_list, autoscale_axis)

    if legend_subplot is not None:
        ax = ax_list[i]
        leg_stuff = ax.get_legend_handles_labels()
        pl.legend(*leg_stuff, loc='center left', bbox_to_anchor=(0.9, 0.5),
                  bbox_transform=pl.gcf().transFigure,
                  title=legend_title)


###################
#### HEAT MAPS ####
###################

def plot_heat_map(z, include_values=False,
                  cmap=matplotlib.cm.Reds,
                  ax=None,
                  xlabel='auto', ylabel='auto',
                  xtick_labels='auto', ytick_labels='auto',
                  xtick_locs=None, ytick_locs=None,
                  xtick_kwargs={}, ytick_kwargs={},
                  clabel_pos='top',
                  transpose_y=False, convert_to_log_scale=False,
                  show_colorbar=False, colorbar_dict={},
                  values_format='{:.2}', values_font_size='small',
                  values_color=None, values_text_kw={},
                  bad_color=None,
                  **kwargs):
    """
    Plots a heat map of z.

    Parameters
    -------------

    z : ndarray | DataFrame
    ax : None # NOT IMPLEMENTED YET
        Axis to be used. If None uses the current axis.
    xlabel : str | 'auto' | None
        name for the x-axis
    ylabel : str | 'auto' | None
        name for the y-axis
    xtick_labels : list of str
        names for the columns
    ytick_labels : list of str
        names for the rows
    transpose_y : bool
        Flips the data along the y axis if true
    convert_to_log_scale : bool
        If true, plots the log of z.
    clabel_pos : 'top' | 'bottom'
        Location of the column labels. Default is 'top'.
    cmap : colormap | str
        colormap to use for plotting the values; e.g., matplotlib.cmap.Blues,
        if str then expecting something like 'Blues' to look up using getattr(matplotlib.cm, ...)
    values_color : None | color
        if None, coloring will be the inverse of cmap
        Otherwise the color given would be used for the text color of all the values.
    bad_color : color
        This is the color that will be used for nan values

    Returns
    ---------------
    Output from matshow command (matplotlib.image.AxesImage)
    """
    # TODO: Add possibility to change rotation, size, etc. of xtick markers
    # TODO: Rename in API : xtick_labels and ytick_labels
    # TODO: Implement ax

    # Setting default font sizes
    xtick_kwargs.setdefault('fontsize', 'large')
    ytick_kwargs.setdefault('fontsize', 'large')

    ##
    # Figure out annotation for axes based on data frame.
    # DataFrame annotation is used only if 'auto' was given
    # to the annotation.
    auto_col_name, auto_col_labels, auto_row_name, auto_row_labels = extract_annotation(z)

    if xtick_labels is 'auto': xtick_labels = auto_col_labels
    if ytick_labels is 'auto': ytick_labels = auto_row_labels
    if xlabel is 'auto': xlabel = auto_col_name
    if ylabel is 'auto': ylabel = auto_row_name

    if isinstance(z, pandas.DataFrame):
        values = z.values
    else:
        values = z

    if convert_to_log_scale:
        values = numpy.log(values)

    if transpose_y:
        values = numpy.flipud(values)

    if isinstance(cmap, str):
        cmap = getattr(cm, cmap)

    old_ax = plt.gca()

    if ax is not None:
        plt.sca(ax)
    else:
        ax = plt.gca()

    output = ax.matshow(values, cmap=cmap, **kwargs)

    #####
    # Make the colorbar pretty
    #
    if show_colorbar:
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        divider = make_axes_locatable(ax)

        colorbar_dict.setdefault('size', "5%")
        colorbar_dict.setdefault('pad', 0.05)
        cax = divider.append_axes("right", **colorbar_dict)
        cb = plt.colorbar(output, cax=cax)
        plt.sca(ax)  # Switch back to original axes

    #######
    # Annotate the heat amp
    #
    if xtick_labels is not None and len(xtick_labels) > 0:
        if xtick_locs:
            plt.xticks(xtick_locs, xtick_labels, **xtick_kwargs)
        else:
            plt.xticks(range(len(xtick_labels)), xtick_labels, **xtick_kwargs)

    if ytick_labels is not None and len(ytick_labels) > 0:
        if ytick_locs:
            plt.yticks(ytick_locs, ytick_labels, **ytick_kwargs)
        else:
            plt.yticks(range(len(ytick_labels)), ytick_labels, **ytick_kwargs)

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    if include_values:
        def text_cmap(x):
            if numpy.isnan(x):
                return cmap(1.0)
            if x > 0.2 and x < 0.5:
                x = 0.2
            if x < 0.8 and x >= 0.5:
                x = 0.8
            return cmap(1.0 - x)

        values_text_kw['fontsize'] = values_font_size
        values_text_kw['color'] = values_color
        plot_table(values, text_format=values_format, cmap=text_cmap, **values_text_kw)

    # Changes the default position for the xlabel to the 'top'
    xaxis = ax.xaxis

    if clabel_pos == 'top':
        xaxis.set_label_position('top')
        xaxis.tick_top()
    else:
        ax.xaxis.tick_bottom()
        ax.xaxis.set_label_position('bottom')

    ##
    # Can get rid of the part below when the part above
    # is rewritten so that changes are applied specifically to the axes
    # object rather than using the method interface.
    plt.sca(old_ax)

    return output


def plot_table(matrix, text_format='{:.2f}', cmap=None, **kwargs):
    """
    Plots a numpy matrix as a table. Uses the current axis bounding box to decide on limits.
    text_format specifies the formatting to apply to the values.

    Parameters
    ----------

    matrix : ndarray

    text_format : str
        Indicates how to format the the values
        text_format = {:.2} -> keeps all digits until the first 2 significant digits past the decimal
        text_format = {:.2f} -> keeps only 2 digits past the decimal

    cmap : None | colormap
        if a colormap is provided, this colormap will be used to choose the color of the text.

    **kwargs : all other arguments passed to plt.text function

    Examples
    ----------

    plot_table(numpy.random.random((3,3))
    plt.show()

    """
    shape = matrix.shape

    xtick_pos = numpy.arange(shape[1])
    ytick_pos = numpy.arange(shape[0])

    xtick_grid, ytick_grid = numpy.meshgrid(xtick_pos, ytick_pos)

    vmax = numpy.nanmax(matrix)
    vmin = numpy.nanmin(matrix)

    if not kwargs.get('color', None) and cmap is not None:
        use_cmap = True
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
    else:
        use_cmap = False

    for (row, col), w in numpy.ndenumerate(matrix):
        x = xtick_grid[row, col]
        y = ytick_grid[row, col]

        if use_cmap:
            kwargs['color'] = cmap(norm(w))

        plt.text(x, y, text_format.format(w), horizontalalignment='center',
                 verticalalignment='center', transform=plt.gca().transData, **kwargs)


################################
#### PLOTTING VECTOR FIELDS ####
################################

from matplotlib.patches import ConnectionPatch


def plot_arrow_path(x_coordinates, y_coordinates, arrowstyle="fancy", **kwargs):
    """
    Draws a path of arrows following the path of the coordinates.

    Note: This is just a wrapper around matplotlib's ConnectionPath, which at the moment does not add much functionality.

    Parameters
    ------------------
    x_coordinates : ndarray or list
        X coordinates
    y_coordinates : ndarray or list
        Y coordinates
    arrowstyle : str
        'fancy', '->', look up other ones on matplotlib's page.
    kwargs : keyword arguments passed to ConnectionPath

    Returns
    ---------------

    list
        arrow patches added

    Example
    ---------------

    x = [1, 2, 5, 1]
    y = [0, 3, 1, 2]

    graph.plot_arrow_path(x, y, arrowstyle='fancy', color=color, alpha=0.5, shrinkA=2, shrinkB=4);

    xlim(0, 5) # it's necessary to set limits, not autorelimiting after using this function!
    ylim(0, 5)
    """
    position_list = zip(x_coordinates, y_coordinates)
    ax = kwargs.pop('ax', pl.gca())

    patch_list = []

    for index in range(len(position_list) - 1):
        con = ConnectionPatch(xyA=position_list[index], xyB=position_list[index + 1],
                              coordsA="data", coordsB="data",
                              axesA=ax, axesB=ax, arrowstyle=arrowstyle, **kwargs)
        patch_list.append(con)
        ax.add_artist(con)
    return patch_list


###############################
## BEAUTIFICATION OF PLOTS ####
###############################

# -- Defaults --- #

def set_pretty_defaults(linewidth=6, marker='o', markersize=25, xlabelsize=14, ylabelsize=14,
                        fontsize=16):
    """ Sets plotting defaults for matplotlib library """
    plt.rcParams['xtick.labelsize'] = 16.0
    plt.rcParams['ytick.labelsize'] = 16.0
    plt.rcParams['axes.labelsize'] = 16.0
    plt.rcParams.update({'font.size': fontsize})
    # plt.rc('lines', linewidth=2, marker='o', markersize=15)
    # plt.rc('mathtext', default='regular')
    # plt.rc('text', usetex=True)
    # subplots_adjust(top=top, wspace= wspace, hspace = hspace ,  left=left, right = right, bottom=bottom)
    # rc('lines', linewidth= linewidth, marker= marker, markersize= markersize)


# -- Legends --- #

def move_legend_outside(legend, ax=None, scalewidth=0.8):
    """ Moves the current legend outside of the figure """
    if not ax:
        ax = plt.gca()

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * scalewidth, box.height])
    legend.set_bbox_to_anchor((1, 0.5))


def adjust_legend_fonts(legend, titlesize=20, textsize=20):
    """ Allows to adjust the size of fonts used in the legend. """
    ltext = legendReference.get_texts()  # all the text.Text instance in the legend
    legendReference.get_title().set_size(titlesize)
    plt.setp(ltext, fontsize=textsize)  # the legend text fontsize


# -- Other --- #
def array2colors(x, cmap=cm.jet, **kwargs):
    '''
    Return rgba colors corresponding to values of x from desired colormap.
    Inputs:
        x         = 1D iterable of strs/floats/ints to be mapped to colors.
        cmap      = either color map instance or name of colormap as string.
        vmin/vmax = (optional) float/int min/max values for the mapping.
                    If not provided, set to the min/max of x.
    Outputs:
        colors = array of rgba color values. each row corresponds to a value in x.
    '''
    from matplotlib.colors import rgb2hex
    ## get the colormap
    if type(cmap) is str:
        if cmap not in cm.datad: raise ValueError('Unkown colormap %s' % cmap)
        cmap = cm.get_cmap(cmap)

    x = np.asarray(x)
    isstr = np.issubdtype(x.dtype, str)
    if isstr:
        temp = np.copy(x)
        x_set = set(x)
        temp_d = dict((val, i) for i, val in enumerate(x_set))
        x = [temp_d[id] for id in temp]
    ## get the color limits
    vmin = kwargs.get('vmin', np.min(x))
    vmax = kwargs.get('vmax', np.max(x))
    ## set the mapping object
    t = cm.ScalarMappable(cmap=cmap)
    t.set_clim(vmin, vmax)
    ## get the colors
    colors = t.to_rgba(x)
    if hex:
        colors = [rgb2hex(c) for c in colors]
    return colors


def label_subplot(subplot_number, size=30, xloc=-0.17, yloc=1.15, transform='axes', **args):
    """ Labels the plot with the correct subplot number at the specified position and specified font size.
        (The idea is to get something that will place the labels consistently and in a "good" location.)
        Good numbers
        If using axes:
            xloc=-0.17, yloc=1.15
        If using figure:
            #xloc=-0.17, yloc=1.15
    """
    label = docstring.ascii_uppercase[subplot_number]

    if transform == 'axes':
        transform = plt.gca().transAxes
    else:
        transform = plt.gcf().transFigure

    plt.text(xloc, yloc, label, size=size, horizontalalignment='center', verticalalignment='center',
             transform=transform, weight='bold', **args)


#############
#### MISC ###
#############

def increase_linewidth_for_matrix_printing():
    """ Increases the linewidth allowed for printing numpy matrices. """
    numpy.set_printoptions(linewidth=200, precision=4)


def savefig(figname, output_dir='./Figures/', tictoc=False, formats=['.jpg'], **kwargs):
    """
    A wrapper around matplotlibs savefig function.
    Automatically places figures in the output_dir path.
    Saves the current figure several different formats.
    """
    util.ensure_directory(output_dir)
    if tictoc:
        figname = figname + '_%0.2f' % time.time()

    cleanName = re.sub('[^a-zA-Z0-9_-]', '', figname)

    for thisFormat in formats:
        plt.gcf().savefig(os.path.join(output_dir, cleanName) + thisFormat, **kwargs)


def set_pretty_terminal_output():
    """ Need to retire this function (just change the name) """
    increase_linewidth_for_matrix_printing()


##############################
#### FITTINGS AND PLOTTING ###
##############################

def fit_and_plot(xdata, ydata, xfit, xy=None):
    """
    The goal of this function is to accept data, and instructions for a simple fit, and plot
    both the data and the results.

    This function needs more work to be useful.

    TODO: Make into polynomial rather than just linear.
    """
    xdata, ydata = removeNaNs(xdata, ydata)
    coefs = numpy.polyfit(xdata, ydata, 1)
    yfit = numpy.polyval(coefs, xfit)
    print('Fit coefficients: ', coefs)

    # Plot Fit
    plt.plot(xfit, yfit, '--r', linewidth=2)

    if xy is not None:
        x, y = xy
    else:
        x = 0.05
        y = 0.90
    plt.text(x, y, 'y = m x + b\n(m,b) = (%.2f, %0.2f)' % (coefs[0], coefs[1]),
             transform=plt.gca().transAxes)


def plot_histogram(data, **kwargs):
    """
    Plots a histogram.
    Filters out nan data.
    Plots the mean and standard deviation.
    """
    nanIndexes = numpy.isnan(data)
    dataClean = data[~nanIndexes].flatten()

    n, bins, patches = plt.hist(dataClean, **kwargs)
    d_mean = numpy.mean(dataClean)  # calculate mean
    d_std = numpy.std(dataClean)  # calculate standard deviation
    plt.text(0.5, 0.95,
             r'$\mu=$' + '{0:0.2f}'.format(d_mean) + r', $\sigma=$' + '{0:0.2f}'.format(d_std),
             transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='center')
    return d_mean, d_std


#############################
#### INTERNAL FUNCTIONS #####
#############################

def set_tick_lines_visibility(ax, visible=True):
    """
    Sets the visibility of the tick lines of the requested axis.
    """
    for i, thisAxis in enumerate((ax.get_xaxis(), ax.get_yaxis())):
        for thisItem in thisAxis.get_ticklines():
            if isinstance(visible, list):
                thisItem.set_visible(visible[i])
            else:
                thisItem.set_visible(visible)


def set_tick_labels_visibility(ax, visible=True):
    """
    Sets the visibility of the tick labels of the requested axis.
    """
    for i, thisAxis in enumerate((ax.get_xaxis(), ax.get_yaxis())):
        for thisItem in thisAxis.get_ticklabels():
            if isinstance(visible, list):
                thisItem.set_visible(visible[i])
            else:
                thisItem.set_visible(visible)


def hide_axes(axes, hide=True):
    set_tick_lines_visibility(axes, not hide)
    set_tick_labels_visibility(axes, not hide)


def extract_annotation(data):
    """ Extracts names and values of rows and columns.

    Parameter
    ------------
    data : DataFrame | Panel

    Returns
    -----------
    col_name, col_values, row_name, row_values
    """
    xlabel = None
    xvalues = None
    ylabel = None
    yvalues = None
    if hasattr(data, 'minor_axis'):
        xvalues = data.minor_axis
        if hasattr(data.minor_axis, 'name'):
            xlabel = data.minor_axis.name
    if hasattr(data, 'columns'):
        xvalues = data.columns
        if hasattr(data.columns, 'name'):
            xlabel = data.columns.name
    if hasattr(data, 'major_axis'):
        yvalues = data.major_axis
        if hasattr(data.major_axis, 'name'):
            ylabel = data.major_axis.name
    if hasattr(data, 'index'):
        yvalues = data.index
        if hasattr(data.index, 'name'):
            ylabel = data.index.name
    return xlabel, xvalues, ylabel, yvalues


################################
### TEMPORARY TEST FUNCITONS ###
################################

def get_slice(panel, row, col):
    ndim = len(panel.shape)
    nrange = arange(ndim)
    nrange = list(nrange[(nrange - 2) % ndim])  # Moves the last two dimensions to the first two
    data_slice = panel.transpose(*nrange).iloc[row].iloc[col]
    return data_slice
