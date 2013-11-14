''''
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
'''
from numpy import (log, log10, exp, where, sign, vectorize, 
                   min, max, linspace, logspace, r_, abs, asarray)
from scipy.optimize import brentq
from scipy.interpolate import InterpolatedUnivariateSpline
from GoreUtilities.util import to_list
_machine_max = 2**18
_l_mmax = log10(_machine_max)
_display_max = 10**4


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
        (If old range is not given use the one specified in self.meta['_channels_']['$PnR']) Depracated!!!
    """
#     if old_range is None:
#         m = self.get_meta()['_channels_']
#         old_range = m['$PnR'].astype(float)
#         old_range.index = self.channel_names
    y = x/old_range*new_range
    return y

rescale = linear

def tlog(x, th=1, r=_display_max, d=_l_mmax):
    '''
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
    '''
    if th<=0:
        raise ValueError, 'Threshold value must be positive. %s given.' %th
    return where(x<=th, log10(th) * 1.*r/d, log10(x) * 1.*r/d)

def tlog_inv(y, th=1, r=_display_max, d=_l_mmax):
    '''
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
    '''
    if th<=0:
        raise ValueError, 'Threshold value must be positive. %s given.' %th
    x = 10**(y * 1.*d/r)
    try:
        x[x<th] = th
    except TypeError:
        if x<th: x = th
    return x 

def glog(x, l):
    '''
    Natural base generalized-log transform. 
    '''
    return log(x + (x**2 + l)**0.5)

def glog_inv(y,l):
    ey = exp(y)
    return (ey**2 - l)/(2*ey) 

def hlog_inv(y, b=500, r=_display_max, d=_l_mmax):
    '''
    Inverse of base 10 hyperlog transform.
    '''
    aux = 1.*d/r *y
    s = sign(y)
    if s.shape: # to catch case where input is a single number
        s[s==0] = 1
    elif s==0:
        s = 1
    return s*10**(s*aux) + b*aux - s

def _x_for_spln(x, nx):
    '''
    Create vector of logarithmically spaced values to be used in constructing a spline.
    Resulting values span the range the input 'x'. 
    To extend to negative values, the spacing is done separately on the 
    negative and positive range, and these are later combined.
    The number of points in the negative/positive range is proportional
    to their relative range in log space. i.e., for data in the range
    [-100, 1000] 2/5 of the resulting points will be in the negative range. 
    '''
    x = asarray(x)
    xmin = min(x)
    xmax = max(x)
    if xmin==xmax:
        return asarray([xmin]*nx)
    if xmax<=0: #all values<=0
        return -_get_x_spln(-x, nx)[::-1]
    lxmax = log10(xmax)
    lxmin = log10(abs(xmin))
    if xmin>0:
        x_spln = logspace(lxmin, lxmax, nx)
    elif xmin==0:
        x_spln = r_[0, logspace(-1, lxmax, nx)]
    else:
        f     = lxmin/(lxmin+lxmax)
        nx_neg = int(f*nx)
        nx_pos = nx - nx_neg
        x_spln_pos  = logspace(-1, lxmax, nx_pos)
        x_spln_neg  = -logspace(-1, lxmin, nx_neg)[::-1]
        x_spln      = r_[x_spln_neg, x_spln_pos]
    return x_spln


def _make_hlog_numeric(b, r, d):
    '''
    Return a function that numerically computes the hlog transformation for given parameter values.
    '''
    hlog_obj = lambda y, x, b, r, d: hlog_inv(y, b, r, d) - x
    find_inv = vectorize(lambda x: brentq(hlog_obj, -2*r, 2*r, 
                                        args=(x, b, r, d)))
    return find_inv 

def _make_hlog_spln(x, b=500, r=_display_max, d=_l_mmax, nx=1000, **kwargs):
    '''
    Construct a spline interpolation of the hlog transformation with given parameters.
    '''
    # create x values for spline
    x_spln = _get_x_spln(x, nx)
    #make spline
    hlog_fun = _make_hlog_numeric(b, r, d)
    y_spln = hlog_fun(x_spln)
    spln = InterpolatedUnivariateSpline(x_spln, y_spln, **kwrgs)
    return spln

def hlog(x, b=500, r=_display_max, d=_l_mmax, 
        use_spln=None, spln_min=1000, spln_nx=1000, spln_kwrgs={}):
    '''
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
    use_spln : bool | None
        Determines whether to transform fewer points and use spline 
        interpulation to get all transformed values. This is a speed hack.
        If None, set based on the number of points to be transformed.
    spln_min : num
        If transforming more than spln_min points, transform fewer points
        and use spline interpulation to get all transformed values.
        This is just a speed hack.
    spln_nx : int
        number of points to use to construct spline
    spln_kwrgs :
        kwrgs for scipy.interpolate.InterpolatedUnivariateSpline    
    
    Returns
    -------
    Array of transformed values.
    '''
    hlog_fun = _make_hlog_numeric(b, r, d)
    if not hasattr(x, '__len__'): #if transforming a single number
        y = hlog_fun(x)
    else:
        n = len(x)
        if not n: #if transforming empty container
            return x
        ## decide whether to use spline or not
        if use_spln is None: 
            if n>=spln_min:
                use_spln = True
            else:
                use_spln = False
        ## do transform
        if use_spln:
            spln = _make_hlog_spln(x, b, r, d, spln_nx=1000, **spln_kwrgs)
            y = spln(x)
        else:
            y = hlog_fun(x)
    return y


_canonical_names = {
'linear':   'linear',
'lin':      'linear',
'rescale':  'linear',
'hlog':     'hlog',
'hyperlog': 'hlog',
'glog':     'glog',
'tlog':     'tlog',
}

def _get_canonical_name(name):
    try: 
        name = name.lower()
    except AttributeError:
        pass
    return _canonical_names.get(name, None)

name_transforms = {
'linear': {'forward':linear, 'inverse':linear},
'hlog'  : {'forward':hlog, 'inverse':hlog_inv},
'glog'  : {'forward':glog, 'inverse':glog_inv},
'tlog'  : {'forward':tlog, 'inverse':tlog_inv},
}

def parse_transform(transform, direction='forward'):
    '''
    direction : 'forward' | 'inverse'
    '''
    if hasattr(transform, '__call__'):
        tfun = transform
    elif hasattr(transform, 'lower'):
        tname = _get_canonical_name(transform)
        if tname is None:
            raise ValueError, 'Unknown transform: %s' %transform
        else:
            tfun = name_transforms[tname][direction]        
    else:
        raise TypeError, 'Unsupported transform type: %s' %type(transform)
    return tfun


def transform_frame(frame, transform, columns=None, direction='forward',
                     return_all=True, args=(), **kwargs):
    '''
    Apply transform to specified columns. 
    
    direction: 'forward' | 'inverse'
    return_all: bool
        True -  return all columns, with specified ones transformed.
        False - return only specified columns.
    
    TODO: add detailed doc
    '''
    tfun = parse_transform(transform, direction)
    columns = to_list(columns)
    if columns is None:
        columns = frame.columns
    if return_all:
        transformed = frame.copy()
        for c in columns:
            transformed[c] = tfun(frame[c],  *args, **kwargs) 
    else:
        transformed = frame.filter(columns).apply(tfun, *args, **kwargs)
    return transformed

from GoreUtilities import BaseObject
class Transformation(BaseObject):
    
    def __init__(self, transform, direction='forward', name=None, args=(), **kwargs):
        '''
        A transformation for flow cytometry data. 
        
        Parameters
        ----------
        transform: callable | str
            Callable that does a transformation (should accept a number or array),
            or one of the supported named transformations.
            Supported transformation are: {}. 
        direction: 'forward' | 'inverse'
        '''
        self.tfun   = parse_transform(transform, direction)
        self.transform = transform
        self.direction = direction
        self.args   = args
        self.kwargs = kwargs
        self.name   = name
    
    __init__.__doc__ = __init__.__doc__.format(', '.join(name_transforms.keys()))
    
    def __repr__(self): return repr(self.name)
        
    def __call__(self, x):
        '''
        Apply transform to x
        '''
        return self.tfun(x,  *self.args, **self.kwargs)
    
    @property
    def inverse(self):
        tname = _get_canonical_name(self.transform)
        if tname is None:
            warnings.warn('inverse is supported only for named transforms. Returning None.')
            return None
        else:
            direction = 'forward' if self.direction=='inverse' else 'inverse'
            ifun = name_transforms[tname][direction] 
            tinv = self.copy()
            tinv.tfun = ifun
            tinv.direction = direction
        return tinv

        
if __name__ == '__main__':
#     y1 = -1
#     y2 = 100
#     x1 = hlog_inv(y1)
#     x2 = hlog_inv(y2)
#     print x1, x2
#     print hlog(x1)
#     print hlog(x2)
#     print hlog([x1,x2])
#     
#     n = 2000
#     y = linspace(-_display_max, _display_max, n)
#     x = hlog_inv(y)
#     print x, '\n', y
#     print hlog(x)

    import numpy as np
    x = np.random.rand(3,2)*100
    t = Transformation('hlog', 'forward', b=5, r=3)
    tinv = t.inverse
    
    print x
    print tinv(t(x))
