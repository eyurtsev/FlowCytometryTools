import os
import unittest

from fcsparser import parse
import numpy as np
from numpy.testing import assert_array_almost_equal

from .. import test_data_file

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestFCSParser(unittest.TestCase):
    def test_parse(self):
        """Verify that the fcs parser behaves as expected."""
        self.maxDiff = None
        meta = parse(test_data_file, meta_data_only=True)

        expected_meta = {
            u'$BEGINANALYSIS': u'0',
            u'$BEGINDATA': u'1892',
            u'$BEGINSTEXT': u'0',
            u'$BTIM': u'11:47:24',
            u'$BYTEORD': u'1,2,3,4',
            u'$CELLS': u'PID_101_MG1655_Transformants_D01',
            u'$CYT': u'MACSQuant',
            u'$CYTSN': u'3057',
            u'$DATATYPE': u'F',
            u'$DATE': u'2013-Jul-19',
            u'$ENDANALYSIS': u'0',
            u'$ENDDATA': u'641891',
            u'$ENDSTEXT': u'0',
            u'$ETIM': u'11:47:46',
            u'$FIL': u'EY_2013-07-19_PID_101_MG1655_Transformants_D01_Well_A3.001.fcs',
            u'$MODE': u'L',
            u'$NEXTDATA': 0,
            u'$OP': u'Eugene',
            u'$P10B': 32,
            u'$P10E': u'0.000000,0.000000',
            u'$P10G': u'1',
            u'$P10N': u'V2-W',
            u'$P10R': u'262144',
            u'$P10S': u'V2-W',
            u'$P11B': 32,
            u'$P11E': u'0.000000,0.000000',
            u'$P11G': u'1',
            u'$P11N': u'Y2-A',
            u'$P11R': u'262144',
            u'$P11S': u'Y2-A',
            u'$P12B': 32,
            u'$P12E': u'0.000000,0.000000',
            u'$P12G': u'1',
            u'$P12N': u'Y2-H',
            u'$P12R': u'262144',
            u'$P12S': u'Y2-H',
            u'$P13B': 32,
            u'$P13E': u'0.000000,0.000000',
            u'$P13G': u'1',
            u'$P13N': u'Y2-W',
            u'$P13R': u'262144',
            u'$P13S': u'Y2-W',
            u'$P14B': 32,
            u'$P14E': u'0.000000,0.000000',
            u'$P14G': u'1',
            u'$P14N': u'B1-A',
            u'$P14R': u'262144',
            u'$P14S': u'B1-A',
            u'$P15B': 32,
            u'$P15E': u'0.000000,0.000000',
            u'$P15G': u'1',
            u'$P15N': u'B1-H',
            u'$P15R': u'262144',
            u'$P15S': u'B1-H',
            u'$P16B': 32,
            u'$P16E': u'0.000000,0.000000',
            u'$P16G': u'1',
            u'$P16N': u'B1-W',
            u'$P16R': u'262144',
            u'$P16S': u'B1-W',
            u'$P1B': 32,
            u'$P1E': u'0.000000,0.000000',
            u'$P1G': u'1',
            u'$P1N': u'HDR-T',
            u'$P1R': u'262144',
            u'$P1S': u'HDR-T',
            u'$P2B': 32,
            u'$P2E': u'0.000000,0.000000',
            u'$P2G': u'1',
            u'$P2N': u'FSC-A',
            u'$P2R': u'262144',
            u'$P2S': u'FSC-A',
            u'$P3B': 32,
            u'$P3E': u'0.000000,0.000000',
            u'$P3G': u'1',
            u'$P3N': u'FSC-H',
            u'$P3R': u'262144',
            u'$P3S': u'FSC-H',
            u'$P4B': 32,
            u'$P4E': u'0.000000,0.000000',
            u'$P4G': u'1',
            u'$P4N': u'FSC-W',
            u'$P4R': u'262144',
            u'$P4S': u'FSC-W',
            u'$P5B': 32,
            u'$P5E': u'0.000000,0.000000',
            u'$P5G': u'1',
            u'$P5N': u'SSC-A',
            u'$P5R': u'262144',
            u'$P5S': u'SSC-A',
            u'$P6B': 32,
            u'$P6E': u'0.000000,0.000000',
            u'$P6G': u'1',
            u'$P6N': u'SSC-H',
            u'$P6R': u'262144',
            u'$P6S': u'SSC-H',
            u'$P7B': 32,
            u'$P7E': u'0.000000,0.000000',
            u'$P7G': u'1',
            u'$P7N': u'SSC-W',
            u'$P7R': u'262144',
            u'$P7S': u'SSC-W',
            u'$P8B': 32,
            u'$P8E': u'0.000000,0.000000',
            u'$P8G': u'1',
            u'$P8N': u'V2-A',
            u'$P8R': u'262144',
            u'$P8S': u'V2-A',
            u'$P9B': 32,
            u'$P9E': u'0.000000,0.000000',
            u'$P9G': u'1',
            u'$P9N': u'V2-H',
            u'$P9R': u'262144',
            u'$P9S': u'V2-H',
            u'$PAR': 16,
            u'$SRC': u'A3',
            u'$SYS': u'MACSQuantify,2.4.1247.1dev',
            u'$TOT': 10000,
            '__header__': {'FCS format': b'FCS3.0',
                           'analysis end': 0,
                           'analysis start': 0,
                           'data end': 641891,
                           'data start': 1892,
                           'text end': 1824,
                           'text start': 256}
        }
        self.assertEqual(meta, expected_meta)

        meta, df = parse(test_data_file, meta_data_only=False)

        self.assertEqual(meta, expected_meta)

        expected_columns = [u'HDR-T', u'FSC-A', u'FSC-H', u'FSC-W', u'SSC-A', u'SSC-H',
                            u'SSC-W', u'V2-A', u'V2-H', u'V2-W', u'Y2-A', u'Y2-H', u'Y2-W',
                            u'B1-A', u'B1-H', u'B1-W']
        self.assertListEqual(df.columns.tolist(), expected_columns)

        # Verify that a few selected value fo the data resolve to their expected values.
        subset_of_data = df.iloc[:3, :3].values

        expected_values = np.array([[2.0185113, 459.96298, 437.35455],
                                    [27.451754, -267.17465, 365.35455],
                                    [32.043865, -201.58234, 501.35455]], dtype=np.float32)

        assert_array_almost_equal(subset_of_data, expected_values)
