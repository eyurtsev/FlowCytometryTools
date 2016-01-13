from __future__ import absolute_import

from FlowCytometryTools._version import version as __version__
from FlowCytometryTools._doc import __doc__

import os
from fcsparser.api import parse as parse_fcs

from FlowCytometryTools.core.containers import FCMeasurement, FCCollection, FCOrderedCollection, FCPlate
from FlowCytometryTools.core.gates import ThresholdGate, IntervalGate, QuadGate, PolyGate
import FlowCytometryTools.core.graph as graph
from FlowCytometryTools.core.graph import plotFCM

_base_path = os.path.dirname(os.path.abspath(__file__))

test_data_dir = os.path.join(_base_path, 'tests', 'data', 'Plate01')
test_data_file = os.path.join(test_data_dir, 'RFP_Well_A3.fcs')
