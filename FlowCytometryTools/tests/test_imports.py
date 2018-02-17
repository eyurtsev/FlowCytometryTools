"""Shallow tests that at least attempt to import some code."""
import unittest


class TestImports(unittest.TestCase):
    def test_imports(self):
        from FlowCytometryTools.gui import dialogs, fc_widget  # noqa
        from FlowCytometryTools.core import (graph, gates, bases, containers, docstring,
                                             transforms)  # noqa
