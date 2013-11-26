from GoreUtilities import util
from matplotlib import docstring

@docstring.Substitution(p='Jason')
def some_function(x):
    """
    %(p)s
    wrote this function
    """

print some_function.__doc__



