try:
    import cPickle as pickle
except ImportError:
    import pickle

import collections
import os

import six


def save(obj, path):
    """
    Pickle (serialize) object to input file path

    Parameters
    ----------
    obj : any object
    path : string
        File path
    """
    with open(path, 'wb') as f:
        try:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print('Pickling failed for object {0}, path {1}'.format(obj, path))
            print('Error message: {0}'.format(e))


def load(path):
    """
    Load pickled object from the specified file path.

    Parameters
    ----------
    path : string
        File path

    Returns
    -------
    unpickled : type of object stored in file
    """
    f = open(path, 'rb')
    try:
        return pickle.load(f)
    finally:
        f.close()


def to_iter(obj):
    """Convert an object to a list if it is not already an iterable.

    Nones are returned unaltered.

    This is an awful function that proliferates an explosion of types, please do not use anymore.
    """
    if isinstance(obj, type(None)):
        return None
    elif isinstance(obj, six.string_types):
        return [obj]
    else:
        # Nesting here since symmetry is broken in isinstance checks.
        # Strings are iterables in python 3, so the relative order of if statements is important.
        if isinstance(obj, collections.Iterable):
            return obj
        else:
            return [obj]


def to_list(obj):
    """
    Converts an object into a list if it not an iterable, forcing tuples into lists.
    Nones are returned unchanged.
    """
    obj = to_iter(obj)

    if isinstance(obj, tuple):
        return list(obj)
    else:
        return obj


#############################
# Working With Files
#############################

def ensure_directory(directory):
    """ Makes a directory if it does not exist already. """
    if not os.path.exists(directory):
        os.makedirs(directory)


#####################
### Base objects ####
#####################

class BaseObject(object):
    """
    Object providing common utility methods.
    Used for inheritance.
    """

    def __repr__(self):
        return repr(self.ID)

    def save(self, path):
        save(self, path)

    @classmethod
    def load(cls, path):
        return load(path)

    @property
    def _constructor(self):
        return self.__class__

    def copy(self, deep=True):
        """
        Make a copy of this object

        Parameters
        ----------
        deep : boolean, default True
            Make a deep copy, i.e. also copy data

        Returns
        -------
        copy : type of caller
        """
        from copy import copy, deepcopy
        if deep:
            return deepcopy(self)
        else:
            return copy(self)
