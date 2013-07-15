''''
Various transformations for flow cytometry data.
The forward transformations all refer to transforming the 
raw data off the machine (i.e. a log transformation is the forword
and an exponential is its inverse).

TODO:
- Add tests!!!! 
- Add references to papers to module and specific functions (including numbers of specific eqs.)
- Add scale parameters (r,d) to glog (if needed?)
- Implement logicle transformation.
'''
from numpy import (log, log10, exp, where, sign, vectorize, 
				   min, max, linspace)

_machine_max = 2**18
_l_mmax = log10(_machine_max)
_display_max = 10**4.5


def tlog(x, th=1, r=_display_max, d=_l_mmax):
	'''
	Truncated log10 transform.
	
	Parameters
	----------
	x : num | num iterable
		values to be transformed.
	th : num
		values below th are transormed to 0.
	r : num (default = 10**4.5)
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
	r : num (default = 10**4.5)
		maximal transformed value.
	d : num (default = log10(2**18))
		log10 of maximal possible measured value.
		tlog_inv(r) = 10**d
		
	Returns
	-------
	Array of transformed values.
	'''
	lr = log10(r)
	return 10**(y * 1.*d/r)

def glog(x, l):
	'''
	Natural base generalized-log transform. 
	'''
	return log(x + (x**2 + l)**0.5)
	
def glog_inv(y,l):
	ey = exp(y)
	return (ey**2 - l)/(2*ey) 

def hlog_inv(y, b=100, r=_display_max, d=_l_mmax):
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

	
def hlog(x, b=100, r=_display_max, d=_l_mmax, 
		spln_min=1000, spln_nx=1000, spln_kwrgs={}):
	'''
	Base 10 hyperlog transform.
	
	Parameters
	----------
	x : num | num iterable
		values to be transformed.
	b : num
		Parameter controling the location of the shift 
		from linear to log transformation.
	r : num (default = 10**4.5)
		maximal transformed value.
	d : num (default = log10(2**18))
		log10 of maximal possible measured value.
		tlog_inv(r) = 10**d
	spln_min :
		If transforming more than spln_min points, transform fewer points
		and use spline interpulation to get all transformed values.
		This is just a speed hack.
	spln_kwrgs :
		kwrgs for scipy.interpolate.InterpolatedUnivariateSpline	
	
	Returns
	-------
	Array of transformed values.
	'''
	from scipy.optimize import brentq
	
	hlog_obj = lambda y, x, b, r, d: hlog_inv(y, b, r, d) - x
	find_inv = vectorize(lambda x: brentq(hlog_obj, -r, r, 
										args=(x, b, r, d)))	
	if not hasattr(x, '__len__'): #if transforming a single number
		y = find_inv(x)
	else:
		n = len(x)
		if n<spln_min:
			y = find_inv(x)
		else:
			from scipy.interpolate import InterpolatedUnivariateSpline
			x_spln = linspace(min(x), max(x), spln_nx)
			y_spln = find_inv(x_spln)
			spln = InterpolatedUnivariateSpline(x_spln, y_spln, **spln_kwrgs)
			y = spln(x)
	return y
	
	
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
	
	
	
	
