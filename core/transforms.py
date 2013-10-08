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

_machine_max = 2**18
_l_mmax = log10(_machine_max)
_display_max = 10**4

def tlog(x, th=1, r=_display_max, d=_l_mmax):
    '''
    Truncated log10 transform.

    Parameters
    ----------
    x : num | num iterable
        values to be transformed.
    th : num
        values below th are transormed to 0.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        tlog(10**d) = r

    Returns
    -------
    Array of transformed values.
    '''
    return where(x<=th, 0, log10(x) * 1.*r/d)

def tlog_inv(y, th=1, r=_display_max, d=_l_mmax):
    '''
    Inverse truncated log10 transform.

    Parameters
    ----------
    y : num | num iterable
        values to be transformed.
    th : num
        values below th are transormed to 0.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        tlog_inv(r) = 10**d

    Returns
    -------
    Array of transformed values.
    '''
    return th * 10**(y * 1.*d/r)

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

def _get_x_spln(x, spln_nx):
    '''
    Create vector of logarithmically spaced values to be used in constructing a spline.
    Resulting values span the range the input 'x'. 
    To extend to negative values, the spacing is done seperatly on the 
    negative and positive range, and these are later combined.
    The number of points in the negative/positive range is proportional
    to their relative range in log space. i.e., for data in the range
    [-100, 1000] 2/5 of the resulting points will be in the negative range. 
    '''
    x = asarray(x)
    xmin = min(x)
    xmax = max(x)
    if xmin==xmax:
        return asarray([xmin]*spln_nx)
    if xmax<=0: #all values<=0
        return -_get_x_spln(-x, spln_nx)[::-1]
    lxmax = log10(xmax)
    lxmin = log10(abs(xmin))
    if xmin>0:
        x_spln = logspace(lxmin, lxmax, spln_nx)
    elif xmin==0:
        x_spln = r_[0, logspace(-1, lxmax, spln_nx)]
    else:
        f     = lxmin/(lxmin+lxmax)
        spln_nx_neg = int(f*spln_nx)
        spln_nx_pos = spln_nx - spln_nx_neg
        x_spln_pos  = logspace(-1, lxmax, spln_nx_pos)
        x_spln_neg  = -logspace(-1, lxmin, spln_nx_neg)[::-1]
        x_spln      = r_[x_spln_neg, x_spln_pos]
    return x_spln

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
        tlog_inv(r) = 10**d
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
    from scipy.optimize import brentq
#     print 'b=',b
    hlog_obj = lambda y, x, b, r, d: hlog_inv(y, b, r, d) - x
    find_inv = vectorize(lambda x: brentq(hlog_obj, -2*r, 2*r, 
                                        args=(x, b, r, d)))    
    if not hasattr(x, '__len__'): #if transforming a single number
        y = find_inv(x)
    else:
        n = len(x)
        if not n:
            return x
        if use_spln is None: 
            #decide whether to use spline or not
            if n>=spln_min:
                use_spln = True
            else:
                use_spln = False
        if use_spln:
            from scipy.interpolate import InterpolatedUnivariateSpline
            # create x values for spline
            x_spln = _get_x_spln(x, spln_nx)
            #make spline
            y_spln = find_inv(x_spln)
            spln = InterpolatedUnivariateSpline(x_spln, y_spln, **spln_kwrgs)
            y = spln(x)
        else:
            y = find_inv(x)
    return y


_canonical_names = {
'hlog':     'hlog',
'hyperlog': 'hlog',
'glog':     'glog',
'tlog':     'tlog',
}

def _get_canonical_name(name):
        return _canonical_names.get(name.lower(), None)

name_transforms = {
'hlog': {'forward':hlog, 'inverse':hlog_inv},
'glog': {'forward':glog, 'inverse':glog_inv},
'tlog': {'forward':tlog, 'inverse':tlog_inv},
}

def get_transform(transform, direction='forward'):
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

def transform_frame(frame, transform, channels=None, direction='forward',
                     return_all=True, args=(), **kwargs):
    '''
    Apply transform to specified channels. 
    
    direction: 'forward' | 'inverse'
    return_all: bool
        True -  return all channels, with specified ones transformed.
        False - return only specified channels.
    
    TODO: add detailed doc
    '''
    tfun = get_transform(transform, direction)
    if channels is None:
        channels = frame.columns
    if isinstance(channels, basestring):
        channels = (channels,)
    if return_all:
        transformed = frame.copy()
        for c in channels:
            transformed[c] = tfun(frame[c],  *args, **kwargs) 
    else:
        transformed = frame.filter(channels).apply(tfun, *args, **kwargs)
    return transformed

if __name__ == '__main__':
    y1 = -1
    y2 = 100
    x1 = hlog_inv(y1)
    x2 = hlog_inv(y2)
    print x1, x2
    print hlog(x1)
    print hlog(x2)
    print hlog([x1,x2])
    
    n = 2000
    y = linspace(-_display_max, _display_max, n)
    x = hlog_inv(y)
    print x, '\n', y
    print hlog(x)

