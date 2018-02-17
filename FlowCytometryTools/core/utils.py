import re
import glob
import os
import fnmatch


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
