from __future__ import absolute_import

from FlowCytometryTools._version import version as __version__
from FlowCytometryTools._doc import __doc__

from fcsparser.api import parse as parse_fcs

from FlowCytometryTools.core.containers import (FCMeasurement, FCCollection, FCOrderedCollection,
                                                FCPlate)
from FlowCytometryTools.core.gates import ThresholdGate, IntervalGate, QuadGate, PolyGate
import FlowCytometryTools.core.graph as graph
from FlowCytometryTools.core.graph import plotFCM


def _get_paths():
    """Generate paths to test data. Done in a function to protect namespace a bit."""
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(base_path, 'tests', 'data', 'Plate01')
    test_data_file = os.path.join(test_data_dir, 'RFP_Well_A3.fcs')
    return test_data_dir, test_data_file


test_data_dir, test_data_file = _get_paths()
