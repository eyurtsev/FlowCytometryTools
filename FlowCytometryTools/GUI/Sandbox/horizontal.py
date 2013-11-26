from pylab import *
from matplotlib.widgets import SpanSelector

x, y = [2, 4, 1], [2, 4, 1]

ax = subplot(111)
ax.plot(x,y)

def onselect(vmin, vmax):
    print vmin, vmax

onselect.A = 'hello'
span = SpanSelector(ax, onselect, 'horizontal')
show()
