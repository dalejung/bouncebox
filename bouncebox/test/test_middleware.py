from unittest import TestCase
from mock import MagicMock

import bouncebox.core.api as bc
import bouncebox.middleware as middleware
reload(middleware)

class TestMiddleWare(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_add_component(self):
        mid = middleware.Middleware()
        child = bc.SeriesComponent()

        # for now, add_component won't work when called on MiddleWare
        try:
            mid.add_component(child)
        except:
            pass
        else:
            assert False

    def test_passthru_down(self):
        parent = bc.Component()
        mid = middleware.Middleware()
        child = bc.Component()

        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()

        mid.add_child(child)
        parent.add_component(mid)

        evt = bc.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)

parent = bc.Component()
mid = middleware.Middleware()
child = bc.Component()

child.add_event_listener(bc.Event, 'handle_event')
child.handle_event = MagicMock()

mid.add_child(child)
parent.add_component(mid)

evt = bc.Event()
parent.broadcast(evt)

if __name__ == '__main__':
    import nose                                                                      
    #nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
    nose.runmodule(argv=[__file__,'-s','-x',],exit=False)   
