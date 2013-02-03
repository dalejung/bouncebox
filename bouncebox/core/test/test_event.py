import unittest
from mock import MagicMock

from bouncebox.core.dispatch import Router, Dispatcher, BaseRouter
import bouncebox.core.event as be

class TestEventA(be.Event):
    pass

class TestEventB(be.Event):
    pass


class TestEvent(unittest.TestCase):
    def setUp(self):
        pass

    def test_class_series(self):
        # error where calling Event.class_series first makes the subclasses
        # inherit and cause error
        be.Event.class_series()
        assert TestEventA.class_series().label_name != TestEventB.class_series().label_name
         

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
