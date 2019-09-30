from __future__ import print_function

import string

from matplotlib import inspect


class FormatDict(dict):
    """Adapted from http://stackoverflow.com/questions/11283961/partial-string-formatting"""

    def __missing__(self, key):
        return "{" + key + "}"


class DocReplacer(object):
    """Decorator object for replacing patterns in docstrings using string.format."""

    def __init__(self, auto_dedent=True, allow_partial_formatting=False, **doc_dict):
        '''
        Parameters
        -------------
        auto_indent : bool
            Flag for automatically indenting the replaced lines to the level of the docstring.
        allow_partial_formatting : bool
            Emnables partial formatting (i.e., not all keys are available in the dictionary)
        doc_dict : kwargs
            Pattern in docstring that a key in this dict will be replaced by the corresponding values.
        Example
        -------------
        TODO: Update this documentation
        @DocReplacer({'p1': 'p1 : int\n\tFirst parameter'})
        def foo(p1):
            """
            Some functions.

            Params:
            {p1}
            """
        will result in foo's docstring being:
            """
            Some functions.

            Params:
            p1 : int
                First parameter
            """
        '''
        self.doc_dict = doc_dict
        self.auto_dedent = auto_dedent
        self.allow_partial_formatting = allow_partial_formatting

    def __call__(self, func):
        if func.__doc__:
            doc = func.__doc__
            if self.auto_dedent:
                doc = inspect.cleandoc(doc)
            func.__doc__ = self._format(doc)
        return func

    def replace(self):
        """Reformat values inside the self.doc_dict using self.doc_dict

        TODO: Make support for partial_formatting
        """
        doc_dict = self.doc_dict.copy()
        for k, v in doc_dict.items():
            if '{' and '}' in v:
                self.doc_dict[k] = v.format(**doc_dict)

    def update(self, *args, **kwargs):
        "Assume self.params is a dict and update it with supplied args"
        self.doc_dict.update(*args, **kwargs)

    def _format(self, doc):
        """ Formats the docstring using self.doc_dict """
        if self.allow_partial_formatting:
            mapping = FormatDict(self.doc_dict)
        else:
            mapping = self.doc_dict
        formatter = string.Formatter()
        return formatter.vformat(doc, (), mapping)
