import unittest

import pandas as pd

from FlowCytometryTools.core.gates import IntervalGate


def _get_indexes_where_true(bool_series):
    """Given a boolean timeseries, return a list of indexes where values are True."""
    return bool_series[bool_series == True].index.tolist()


class TestGates(unittest.TestCase):
    def test_interval_gate(self):
        test_df = pd.DataFrame({'channel': [-1, 0.5, 1.5]}, index=[1, 2, 3])

        test_cases = (
            (0.0, 1.0, ['channel'], 'in', 'gate1', [2]),
            (-10.0, 1.0, ['channel'], 'in', 'gate1', [1, 2]),
            (-10.0, 10.0, ['channel'], 'in', 'gate1', [1, 2, 3]),
            (10.0, 30.0, ['channel'], 'in', 'gate1', []),
            (10.0, 30.0, ['channel'], 'out', 'gate1', [1, 2, 3]),
            (0, 1, ['channel'], 'out', 'gate1', [1, 3]),
            (-10, 10, ['channel'], 'out', 'gate1', []),
        )

        for vert0, vert1, channel_name, region, gate_name, expected_output in test_cases:
            interval_gate = IntervalGate((vert0, vert1), channel_name, region, name=gate_name)
            bool_series = interval_gate._identify(test_df)
            actual_output = _get_indexes_where_true(bool_series)
            self.assertEqual(expected_output, actual_output)

        # Test invalid inputs
        interval_gate = IntervalGate((0, 1), 'invalid channel', 'in')

        with self.assertRaises(KeyError):
            interval_gate._identify(test_df)

        # Invalid interval definition
        with self.assertRaises(ValueError):
            IntervalGate((1, 0), 'invalid channel', 'in')

        # Check that gate behaves correctly with empty dataframe
        empty_df = pd.DataFrame({'channel': []}, index=[])
        gate = IntervalGate((0, 1), ['channel'], 'in')
        self.assertEqual(_get_indexes_where_true(gate._identify(empty_df)), [])
