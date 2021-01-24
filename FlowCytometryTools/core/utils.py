import re
import glob
import os
import fnmatch

try:
    import cPickle as pickle
except ImportError:
    import pickle

import collections

import six


def get_tag_value(string, pre, post, tagtype=float, greedy=True):
    """
    Extracts the value of a tag from a string.

    Parameters
    -----------------

    pre : str
        regular expression to match before the the tag value

    post : str | list | tuple
        regular expression to match after the the tag value

        if list than the regular expressions will be combined into the regular expression (?=post[0]|post[1]|..)

    tagtype : str | float | int
        the type to which the tag value should be converted to

    greedy : bool
        Whether the regular expression is greedy or not.

    Returns
    ---------------
    Tag value if found, None otherwise

    Example
    ------------

    get_tag_value('PID_23.5.txt', pre=r'PID_' , post='(?=_|\.txt)') should return 23.5
    get_tag_value('PID_23.5_.txt', pre=r'PID_', post='(?=_|\.txt)') should return 23.5
    get_tag_value('PID_23_5_.txt', pre=r'PID_', post='(?=_|\.txt)') should return 23
    get_tag_value('PID_23.txt', pre=r'PID_', post='.txt') should return 23
    get_tag_value('PID.txt', pre=r'PID_', post='.txt') should return None
    """
    greedy = '?' if greedy else ''  # For greedy search

    if isinstance(post, (list, tuple)):
        post = '(?=' + '|'.join(post) + ')'

    tag_list = re.findall(r'{pre}(.+{greedy}){post}'.format(pre=pre, post=post, greedy=greedy),
                          string)

    if len(tag_list) > 1:
        raise ValueError('More than one matching pattern found... check filename')
    elif len(tag_list) == 0:
        return None
    else:
        return tagtype(tag_list[0])


def get_files(dirname=None, pattern='*.*', recursive=True):
    """
    Get all file names within a given directory those names match a
    given pattern.

    Parameters
    ----------
    dirname : str | None
        Directory containing the datafiles.
        If None is given, open a dialog box.
    pattern : str
        Return only files whose names match the specified pattern.
    recursive : bool
        True : Search recursively within all sub-directories.
        False : Search only in given directory.

    Returns
    -------
    matches: list
       List of file names (including full path).
    """
    # get dirname from user if not given
    if dirname is None:
        from FlowCytometryTools.gui import dialogs
        dirname = dialogs.select_directory_dialog('Select a directory')

    # find all files in dirname that match pattern
    if recursive:  # search subdirs
        matches = []
        for root, dirnames, filenames in os.walk(dirname):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
    else:
        matches = glob.glob(os.path.join(dirname, pattern))
    return matches


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

    if isinstance(obj, type(None)):
        return None
    else:
        return list(obj)


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
