import os
from ._version import version as __version__
from ._doc import __doc__

from .core.containers import FCMeasurement, FCCollection, FCOrderedCollection, FCPlate
from .core.gates import ThresholdGate, IntervalGate, QuadGate, PolyGate
from .core import graph
from .core.graph import plotFCM

from fcsparser.api import parse as parse_fcs


def _get_paths():
    """Generate paths to test data. Done in a function to protect namespace a bit."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    test_data_dir = os.path.join(base_path, "tests", "data", "Plate01")
    test_data_file = os.path.join(test_data_dir, "RFP_Well_A3.fcs")
    return test_data_dir, test_data_file


test_data_dir, test_data_file = _get_paths()

__all__ = [
    "test_data_dir",
    "test_data_file",
    "parse_fcs",
    "__version__",
    "__doc__",
    "plotFCM",
    "graph",
    "FCCollection",
    "FCMeasurement",
    "FCOrderedCollection",
    "FCPlate",
    "ThresholdGate",
    "IntervalGate",
    "QuadGate",
    "PolyGate",
]
