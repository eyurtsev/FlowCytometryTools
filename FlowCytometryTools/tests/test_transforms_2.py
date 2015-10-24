from unittest import TestCase

import numpy as np

from FlowCytometryTools import FCMeasurement

test_path = '../tests/data/FlowCytometers/HTS_BD_LSR-II/HTS_BD_LSR_II_Mixed_Specimen_001_D6_D06.fcs'


class TestTransforms(TestCase):
    def test_hlog_on_fc_measurement(self):
        fc_measurement = FCMeasurement(ID='test', datafile=test_path)
        fc_measurement = fc_measurement.transform(transform='hlog', b=10)
        data = fc_measurement.data.values[:3, :4]
        correct_output = np.array([[-8.22113965e+03, 1.20259949e+03, 1.01216449e-06,
                                    5.21899170e+03],
                                   [-8.66184277e+03, 1.01013794e+03, 1.01216449e-06,
                                    5.71275928e+03],
                                   [-8.79974414e+03, 1.52737976e+03, 1.01216449e-06,
                                    -4.95852930e+03]])
        np.testing.assert_array_almost_equal(data, correct_output, 5,
                                             err_msg='the hlog transformation gives '
                                                     'an incorrect result')
