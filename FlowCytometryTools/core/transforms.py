"""'
Various transformations for flow cytometry data.
The forward transformations all refer to transforming the
raw data off the machine (i.e. a log transformation is the forword
and an exponential is its inverse).

References:
Bagwell. Cytometry Part A, 2005.
Parks, Roederer, and Moore. Cytometry Part A, 2006.
Trotter, Joseph. In Current Protocols in Cytometry. John Wiley & Sons, Inc., 2001.

TODO:
- Add scale parameters (r,d) to glog (if needed?)
- Implement logicle transformation.
- Add support for transforming a numpy array
"""
from __future__ import division

import warnings

from numpy import (log, log10, exp, where, sign, vectorize, min, max, linspace, logspace, r_, abs,
                   asarray)
from numpy.lib.shape_base import apply_along_axis
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import brentq

from FlowCytometryTools.core.utils import to_list, BaseObject

_machine_max = 2 ** 18
_l_mmax = log10(_machine_max)
_display_max = 10 ** 4


def linear(x, old_range, new_range):
    """
    Rescale each channel to the new range as following:
    new = data/old_range*new_range

    Parameters
    ----------
    data : DataFrame
        data to be rescaled
    new_range : float | array | Series
        Maximal data value after rescaling
    old_range : float | array | Series
        Maximal data value before rescaling
        (If old range is not given use the one specified in self.meta['_channels_']['$PnR'])
        Deprecated!!!
    """
    y = x / old_range * new_range
    return y


rescale = linear


def tlog(x, th=1, r=_display_max, d=_l_mmax):
    """
    Truncated log10 transform.

    Parameters
    ----------
    x : num | num iterable
        values to be transformed.
    th : num
        values below th are transormed to 0.
        Must be positive.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        tlog(10**d) = r

    Returns
    -------
    Array of transformed values.
    """
    if th <= 0:
        raise ValueError('Threshold value must be positive. %s given.' % th)
    return where(x <= th, log10(th) * 1. * r / d, log10(x) * 1. * r / d)


def tlog_inv(y, th=1, r=_display_max, d=_l_mmax):
    """
    Inverse truncated log10 transform.
    Values

    Parameters
    ----------
    y : num | num iterable
        values to be transformed.
    th : num
        Inverse values below th are transormed to th.
        Must be > positive.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        tlog_inv(r) = 10**d

    Returns
    -------
    Array of transformed values.
    """
    if th <= 0:
        raise ValueError('Threshold value must be positive. %s given.' % th)
    x = 10 ** (y * 1. * d / r)
    try:
        x[x < th] = th
    except TypeError:
        if x < th: x = th
    return x


def glog(x, l):
    """
    Natural base generalized-log transform.
    """
    return log(x + (x ** 2 + l) ** 0.5)


def glog_inv(y, l):
    ey = exp(y)
    return (ey ** 2 - l) / (2 * ey)


def hlog_inv(y, b=500, r=_display_max, d=_l_mmax):
    """
    Inverse of base 10 hyperlog transform.
    """
    aux = 1. * d / r * y
    s = sign(y)
    if s.shape:  # to catch case where input is a single number
        s[s == 0] = 1
    elif s == 0:
        s = 1
    return s * 10 ** (s * aux) + b * aux - s


def _x_for_spln(x, nx, log_spacing):
    """
    Create vector of values to be used in constructing a spline.

    Parameters
    ----------
    x : num | num iterable
        Resulted values will span the range [min(x), max(x)]
    nx : int
        Length of returned vector.
    log_spacing: bool
        False - Create linearly spaced values.
        True - Create logarithmically spaced values.
            To extend to negative values, the spacing is done separately on the
            negative and positive range, and these are later combined.
            The number of points in the negative/positive range is proportional
            to their relative range in log space. i.e., for data in the range
            [-100, 1000] 2/5 of the resulting points will be in the negative range.

    Returns
    -------
    x_spln : array
    """
    x = asarray(x)
    xmin = min(x)
    xmax = max(x)
    if xmin == xmax:
        return asarray([xmin] * nx)
    if xmax <= 0:  # all values<=0
        return -_x_for_spln(-x, nx, log_spacing)[::-1]

    if not log_spacing:
        return linspace(xmin, xmax, nx)

    # All code below is to handle-log-spacing when x has potentially both negative
    # and positive values.
    if xmin > 0:
        return logspace(log10(xmin), log10(xmax), nx)
    else:
        lxmax = max([log10(xmax), 0])
        lxmin = max([log10(abs(xmin)), 0])

        # All the code below is for log-spacing, when xmin < 0 and xmax > 0
        if lxmax == 0 and lxmin == 0:
            return linspace(xmin, xmax, nx)  # Use linear spacing as fallback

        if xmin > 0:
            x_spln = logspace(lxmin, lxmax, nx)
        elif xmin == 0:
            x_spln = r_[0, logspace(-1, lxmax, nx - 1)]
        else:  # (xmin < 0)
            f = lxmin / (lxmin + lxmax)
            nx_neg = int(f * nx)
            nx_pos = nx - nx_neg

            if nx <= 1:
                # If triggered fix edge case behavior
                raise AssertionError(u'nx should never bebe 0 or 1')

            # Work-around various edge cases
            if nx_neg == 0:
                nx_neg = 1
                nx_pos = nx_pos - 1

            if nx_pos == 0:
                nx_pos = 1
                nx_neg = nx_neg - 1

            x_spln_pos = logspace(-1, lxmax, nx_pos)
            x_spln_neg = -logspace(lxmin, -1, nx_neg)

            x_spln = r_[x_spln_neg, x_spln_pos]
    return x_spln


def _make_hlog_numeric(b, r, d):
    """
    Return a function that numerically computes the hlog transformation for given parameter values.
    """
    hlog_obj = lambda y, x, b, r, d: hlog_inv(y, b, r, d) - x
    find_inv = vectorize(lambda x: brentq(hlog_obj, -2 * r, 2 * r,
                                          args=(x, b, r, d)))
    return find_inv


def hlog(x, b=500, r=_display_max, d=_l_mmax):
    """
    Base 10 hyperlog transform.

    Parameters
    ----------
    x : num | num iterable
        values to be transformed.
    b : num
        Parameter controling the location of the shift
        from linear to log transformation.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        hlog_inv(r) = 10**d

    Returns
    -------
    Array of transformed values.
    """
    hlog_fun = _make_hlog_numeric(b, r, d)
    if not hasattr(x, '__len__'):  # if transforming a single number
        y = hlog_fun(x)
    else:
        n = len(x)
        if not n:  # if transforming empty container
            return x
        else:
            y = hlog_fun(x)
    return y


_canonical_names = {
    'linear': 'linear',
    'lin': 'linear',
    'rescale': 'linear',
    'hlog': 'hlog',
    'hyperlog': 'hlog',
    'glog': 'glog',
    'tlog': 'tlog',
}


def _get_canonical_name(name):
    try:
        name = name.lower()
    except AttributeError:
        pass
    return _canonical_names.get(name, None)


name_transforms = {
    'linear': {'forward': linear, 'inverse': linear},
    'hlog': {'forward': hlog, 'inverse': hlog_inv},
    'glog': {'forward': glog, 'inverse': glog_inv},
    'tlog': {'forward': tlog, 'inverse': tlog_inv},
}


def parse_transform(transform, direction='forward'):
    """
    direction : 'forward' | 'inverse'
    """
    if hasattr(transform, '__call__'):
        tfun = transform
        tname = None
    elif hasattr(transform, 'lower'):
        tname = _get_canonical_name(transform)
        if tname is None:
            raise ValueError('Unknown transform: %s' % transform)
        else:
            tfun = name_transforms[tname][direction]
    else:
        raise TypeError('Unsupported transform type: %s' % type(transform))
    return tfun, tname


def transform_frame(frame, transform, columns=None, direction='forward',
                    return_all=True, args=(), **kwargs):
    """
    Apply transform to specified columns.

    direction: 'forward' | 'inverse'
    return_all: bool
        True -  return all columns, with specified ones transformed.
        False - return only specified columns.

    .. warning:: deprecated
    """
    tfun, tname = parse_transform(transform, direction)
    columns = to_list(columns)
    if columns is None:
        columns = frame.columns
    if return_all:
        transformed = frame.copy()
        for c in columns:
            transformed[c] = tfun(frame[c], *args, **kwargs)
    else:
        transformed = frame.filter(columns).apply(tfun, *args, **kwargs)
    return transformed


class Transformation(BaseObject):
    """
    A transformation for flow cytometry data.
    """

    def __init__(self, transform, direction='forward', name=None, spln=None, args=(), **kwargs):
        """
        Parameters
        ----------
        transform: callable | str
            Callable that does a transformation (should accept a number or array),
            or one of the supported named transformations.
            Supported transformation are: {}.
        direction: 'forward' | 'inverse'
            Direction of the transformation.
        """
        tfun, tname = parse_transform(transform, direction)
        self.tfun = tfun
        self.tname = tname
        self.direction = direction
        self.args = args
        self.kwargs = kwargs
        self.name = name
        self.spln = spln

    __init__.__doc__ = __init__.__doc__.format(', '.join(name_transforms.keys()))

    def __repr__(self):
        return repr(self.name)

    def transform(self, x, use_spln=False, **kwargs):
        """
        Apply transform to x

        Parameters
        ----------
        x : float-array-convertible
            Data to be transformed.
            Should support conversion to an array of floats.
        use_spln: bool
            True - transform using the spline specified in self.slpn.
                    If self.spln is None, set the spline.
            False - transform using self.tfun
        kwargs:
            Keyword arguments to be passed to self.set_spline.
            Only used if use_spln=True & self.spln=None.

        Returns
        -------
        Array of transformed values.
        """
        x = asarray(x, dtype=float)

        if use_spln:
            if self.spln is None:
                self.set_spline(x.min(), x.max(), **kwargs)
            return apply_along_axis(self.spln, 0, x)
        else:
            return self.tfun(x, *self.args, **self.kwargs)

    __call__ = transform

    @property
    def inverse(self):
        if self.tname is None:
            warnings.warn('inverse is supported only for named transforms. Returning None.')
            return None
        else:
            direction = 'forward' if self.direction == 'inverse' else 'inverse'
            ifun = name_transforms[self.tname][direction]
            tinv = self.copy()
            tinv.tfun = ifun
            tinv.direction = direction
        return tinv

    def set_spline(self, xmin, xmax, nx=1000, log_spacing=None, **kwargs):
        if log_spacing is None:
            if self.tname in ['hlog', 'tlog', 'glog']:
                log_spacing = True
            else:
                log_spacing = False
        x_spln = _x_for_spln([xmin, xmax], nx, log_spacing)
        y_spln = self(x_spln)
        spln = InterpolatedUnivariateSpline(x_spln, y_spln, **kwargs)
        self.spln = spln
