#!/usr/bin/env python
"""
The MIT License (MIT)

Copyright (c) 2013 Eugene Yurtsev and Jonathan Friedman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function

import re
import string
from matplotlib.cbook import dedent

class FormatDict(dict):
    """ Adapted from http://stackoverflow.com/questions/11283961/partial-string-formatting"""
    def __missing__(self, key):
        return "{" + key + "}"

class DocReplacer(object):
    """
    Decorator object for replacing patterns in docstrings using string.format.
    """
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
        self.doc_dict    = doc_dict
        self.auto_dedent = auto_dedent
        self.allow_partial_formatting = allow_partial_formatting

    def __call__(self, func):
        if func.__doc__:
            doc = func.__doc__
            if self.auto_dedent:
                doc = dedent(doc)
            func.__doc__ = self._format(doc)
            #if self.auto_indent:
                # EY: This code does not work for all situations.
                # Breaks when the values in self.doc_dict are non string values
                # Incorrectly located indentation when doc string starts immediately after """
                ### find indentation
                #m = re.search('[ \t]*(?=){.*}', doc)
                #indent = m.group(0).split('{')[0]
                #doc_dict = {}
                #for k,v in self.doc_dict.iteritems():
                    #vlines = v.split('\n')
                    #vnew = vlines[0].lstrip() + ('\n'+indent).join(['']+vlines[1:])
                    #doc_dict[k] = vnew
        return func

    def replace(self):
        """ Reformats values inside the self.doc_dict using self.doc_dict

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

if __name__ == '__main__':
    doc = DocReplacer(a='{b}', b='{a}', c='{a}{b}')
    doc.replace()
    doc.update(a=4)

    @doc
    def f():
        """
        {a}
        {b}
        {c}
        """
    print(f.__doc__)
