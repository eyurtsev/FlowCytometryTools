from _version import version as __version__
from _doc import __doc__

import os
from fcsparser.api import parse as parse_fcs

from core.containers import FCMeasurement, FCCollection, FCOrderedCollection, FCPlate
from core.gates import ThresholdGate, IntervalGate, QuadGate, PolyGate
import core.graph as graph
from core.graph import plotFCM

_base_path = os.path.dirname(os.path.abspath(__file__))

test_data_dir = os.path.join(_base_path, 'tests', 'data', 'Plate01')
test_data_file = os.path.join(test_data_dir, 'RFP_Well_A3.fcs')
