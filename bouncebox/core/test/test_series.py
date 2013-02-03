import unittest
from mock import MagicMock

import bouncebox.core.event as be
import bouncebox.core.series as series

class TestEventA(be.Event):
    pass

class TestEventB(be.Event):
    pass

class TestEventSeries(unittest.TestCase):
    def setUp(self):
        pass

    def test_generate_hash(self):
        """
            Make sure we have different has
        """
        sig_a = TestEventA.class_series()
        sig_b = TestEventB.class_series()
        assert sig_a != sig_b

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
