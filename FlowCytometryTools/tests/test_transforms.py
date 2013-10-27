'''
Created on Dec 20, 2011

@author: jonathanfriedman
'''
import unittest
import numpy as np
from FlowCytometryTools.core import transforms as trans
from numpy.testing import assert_almost_equal, assert_equal

n = 1000
_xmax = 2**18 # max machine value
_ymax = 10**4 # max display value
_xpos = np.logspace(-3, np.log10(_xmax), n)
_xneg = -_xpos[::-1]
_xall = np.r_[_xneg, _xpos]
_ypos = np.logspace(-3, np.log10(_ymax), n)
_yneg = -_ypos[::-1]
_yall = np.r_[_yneg, _ypos]

class TestTransforms(unittest.TestCase):

        def test_tlog(self):
            th = 2
            result = trans.tlog(_xall, th=th)
            self.assertFalse(np.any(result[_xall<th]))
            self.assertTrue(np.all(result[_xall>th]))
            assert_almost_equal(_ymax, result.max())

        def test_tlog_inv(self):
            th = 2
            expected = _xall.copy()
            expected[_xall<=th] = 1
            result = trans.tlog_inv(trans.tlog(_xall, th=th), th=th)
            assert_almost_equal(result, expected)

        def test_get_x_spln(self):
            result = trans._get_x_spln(_xpos, len(_xpos))
            expected = _xpos
            assert_equal(result, expected)

            result = trans._get_x_spln(_xneg, len(_xneg))
            expected = _xneg
            assert_equal(result, expected)

            nx = 10
            result = trans._get_x_spln(0, nx)
            expected = [0]*nx
            assert_equal(result, expected)

            result = trans._get_x_spln(_xall, nx)
            assert_equal(result.min(), _xall.min())
            assert_equal(result.max(), _xall.max())
            assert_equal(len(np.where(result<0)[0]), 
                         len(np.where(result>0)[0]))

        def test_hlog(self):
            hlpos = trans.hlog(_xpos)
            hlneg = trans.hlog(_xneg)
            assert_almost_equal((hlpos[-1]-_ymax)/_ymax,0, decimal=2)
            assert_almost_equal(hlpos, -hlneg[::-1]) #check symmetry
            # test that values get larger as b decreases
            hlpos10 = trans.hlog(_xpos, b=10)
            self.assertTrue( np.all(hlpos10>=hlpos) )
            # check that converges to tlog for large values
            tlpos = trans.tlog(_xpos)
            i = np.where(_xpos>1e4)[0]
            tlpos_large = tlpos[i]
            hlpos_large = hlpos10[i]
            d = (hlpos_large-tlpos_large)/hlpos_large
            assert_almost_equal( d, np.zeros(len(d)), decimal=2)
            # test spline option
            result1 = trans.hlog(_xall, use_spln=True)
            result2 = trans.hlog(_xall, use_spln=False)
            d = (result1-result2)/result1
            assert_almost_equal( d, np.zeros(len(d)), decimal=2)

        def test_hlog_inv(self):
            expected = _xall
            result   = trans.hlog_inv( trans.hlog(_xall) )
            d        = (result-expected)/expected
            assert_almost_equal( d, np.zeros(len(d)), decimal=2)

            result = trans.hlog_inv( trans.hlog(_xall, b=10), b=10 )
            d      = (result-expected)/expected
            assert_almost_equal( d, np.zeros(len(d)), decimal=2)


if __name__ == '__main__':
    import nose
    # nose.runmodule(argv=[__file__,'-vvs','-x', '--ipdb-failure'],
    #                exit=False)
    nose.runmodule(argv=[__file__,'-vvs','-x'],
                   exit=False)
    
    
