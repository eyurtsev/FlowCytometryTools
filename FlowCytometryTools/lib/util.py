#!/usr/bin/env python
try:
    import cPickle as pickle
except ImportError:
    import pickle

import os, glob, csv, inspect, sys, re, fnmatch
import numpy

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
    '''
    Convert an object to a list if it is not already an iterable.
    Nones are returned unaltered.
    '''
    if hasattr(obj, '__iter__'):
        return obj
    elif obj is None:
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
# Working with dictionaries #
#############################

def print_dictionary_as_tree(dictionary, indent=0,
                use_title_style=False, skip_types=False):
    """
    Outputs a pretty tree of a dictionary with its keys.

    Parameters
    -------------
    dictionary : dict
    indent : int
        Number of indentations for each level of nesting
    use_title_style : applies title style formatting for keys
    skip_types : anything
        Describes which types to skip. Note this is a bit confusing now...
        For example, you can set it to numpy.ndarray, then it won't print out any arrays.

    Returns
    --------
    string with formatted output
    """
    out = ''
    for key, value in dictionary.iteritems():
        if use_title_style:
            out += '\t' * indent + str(key).title()
        else:
            out += '\t' * indent + str(key)

        if isinstance(value, dict):
            out += '\n'
            out += print_dictionary_as_tree(value, indent+1)
        elif skip_types is not False and isinstance(value, skip_types):
            out += '\t' * (indent+1) + '!\n'
        else:
            out += '\t' * (indent+1) + str(value) + '\n'
    return out

#############################
# Working With Files
#############################

def ensure_directory(directory):
    """ Makes a directory if it does not exist already. """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_files(dirname=None, pattern='*.*', recursive=True):
    '''
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
    '''
    # get dirname from user if not given
    if dirname is None:
        import dialogs
        dirname = dialogs.select_directory_dialog('Select a directory')

    # find all files in dirname that match pattern
    if recursive: # search subdirs
        matches = []
        for root, dirnames, filenames in os.walk(dirname):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))
    else:
        matches = glob.glob(os.path.join(dirname, pattern))
    return matches

def get_dirname_path_map(path):
    """
    Descends recursively from the specified starting path, and creating a dictionary where
    the keys are the directory names and the values are the full directory paths.

    Parameters
    ----------
    path : str
        starting path

    Returns
    -----------

    Dictionary

    keys - directory names
    values - full paths to directories
    """
    name_path_map = {}
    for root, dirnames, _ in os.walk(path):
        if len(dirnames) > 0:
            for directory in dirnames:
                name_path_map[directory] = os.path.join(root, directory)
    return name_path_map

#def get_tag_folder_map(path, tag, delimiter='_', tag_type=str, recursive=True):
#    """
#    Extracts requested tag from all file that match the pattern and constructs a dictionary
#    between the tags and the file paths.
#    """
#    pass

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
        Whether the regular expression is gredy or not.

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

    TODO Make list/tuple input for pre
    """
    greedy = '?' if greedy else '' # For greedy search

    if isinstance(post, (list, tuple)):
        post = '(?=' + '|'.join(post) + ')'

    tag_list = re.findall(r'{pre}(.+{greedy}){post}'.format(pre=pre, post=post, greedy=greedy), string)

    if len(tag_list) > 1:
        raise ValueError('More than one matching pattern found... check filename')
    elif len(tag_list) == 0:
        return None
    else:
        return tagtype(tag_list[0])

def get_tag_file_map(glob_path, pre, post, tagtype=str, greedy=True):
    """
    Extracts requested tag from all file that match the pattern and constructs a dictionary
    between the tags and the file paths.

    Parameters
    -----------------
    data_path : string
        A path to use for glob. Supports simple regular expressions.

    pre : str
        regular expression to match before the the tag value

    post : str | list | tuple
        regular expression to match after the the tag value

        if list than the regular expressions will be combined into the regular expression (?=post[0]|post[1]|..)

    tagtype : str | float | int
        the type to which the tag value should be converted to
    """
    files = glob.glob(glob_path)
    tag_file_map = {get_tag_value(filepath, pre, post, tagtype=tagtype, greedy=greedy) : filepath for filepath in files}
    return tag_file_map

##############################
## Numpy related functions
##############################
def remove_nans(*data_list):
    """
    Removes corresponding entries when any of the entries is a nan from a list of nd arrays.

    Parameters
    ------------
    data_list = an array of nd arrays

    Returns
    --------
    flattened lists of the nd arrays with all nan elements removed.

    Examples
    --------
    remove_nans([nan, 3, 4, 0], [1, 5, nan, 1]) -> [3, 0], [5, 1]
    """
    data_list = [numpy.array(data) for data in data_list]
    indexes = ~numpy.isnan(data_list[0])
    for data in data_list:
       indexes = numpy.logical_and(indexes, ~numpy.isnan(data))
    return [data[indexes] for data in data_list]

##############################
## Pandas related functions
##############################

def rotate_ndpanel_dimensions(panel, num_rotations, direction='right'):
    """
    Rotates the dimensions of an ndpanel.
    panel : ndpanel
    num_rotations : int
    direction : 'left' | 'right'

    Returns
    ---------

    new nd panel with dimensions rotated
    """
    ndim = len(panel.values.shape)
    nrange = numpy.arange(ndim)

    if direction == 'right' :
        num_rotations = -num_rotations

    nrange = list(nrange[(nrange + num_rotations) % ndim]) # Moves the last two dimensions to the first two
    return panel.transpose(*nrange)


###################################
## Working with git
###################################

def get_git_repository_info(output_format='ipython-html'):
    """
    Produces table summary with information about git repositories associated with loaded python modules.
    (Only for python modules under git control).

    Parameters
    ----------

    output_format : 'DataFrame' | 'ipython-html'

    Returns
    ----------

    a summary table in the specified output_format
    """
    from pandas import DataFrame
    import git

    def get_loaded_git_info():
        """
        For all loaded modules: If the module is under git source control,
        the git working path is recorded together with the git commit, and whether the repository is dirty.

        Returns
        ---------
        Dictionary : keys are git repository paths, values contain all the information
        """
        git_map = {}

        for k, v in sys.modules.items():
            if hasattr(v, '__path__'):
                try:
                    if len(v.__path__) > 0:
                        path = v.__path__[0]
                        repo = git.Repo(path)
                        assert repo.bare == False
                        git_map[repo.working_dir] = (repo.working_dir, os.path.split(repo.working_dir)[1],
                                    str(repo.active_branch), str(repo.commit()), repo.is_dirty())
                except git.InvalidGitRepositoryError:
                    pass
        return git_map

    git_map = get_loaded_git_info()
    data = git_map.values()
    d = DataFrame(numpy.array(data), columns=['Repository Path', 'Folder Name', 'Branch', 'Commit #', 'Dirty?'])

    if output_format == 'DataFrame':
        return d
    elif output_format == 'ipython-html':
        from IPython.display import HTML
        return HTML(d.to_html(index=False))
    else:
        raise ValueError('unrecognized output_format was provided')

#####################
### Base objects ####
#####################

class BaseObject(object):
    '''
    Object providing common utility methods.
    Used for inheritance.
    '''

    def __repr__(self): return repr(self.ID)

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
