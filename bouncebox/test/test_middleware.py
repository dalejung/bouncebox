from unittest import TestCase
from mock import MagicMock

import bouncebox.core.api as bc
import bouncebox.middleware as middleware
import bouncebox.util.testing as testing
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
        child = bc.Component()

        # for now, add_component won't work when called on MiddleWare
        try:
            mid.add_component(child)
        except:
            pass
        else:
            assert False

    def test_add_child(self):
        mid = middleware.Middleware()
        child = bc.Component()

        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()
        
        # add child should be contained=True    
        mid.add_child(child)
        assert child.front is mid

    def test_passthru_down(self):
        parent = bc.Component()
        mid = middleware.Middleware()
        child = bc.Component()

        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()

        # We have an order issue
        parent.add_component(mid)
        mid.add_child(child)

        evt = bc.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)

    def test_passthru_down_reverse(self):
        parent = bc.Component()
        mid = middleware.Middleware()
        child = bc.Component()

        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()

        # NOTE: we add child to mid first
        mid.add_child(child)
        parent.add_component(mid)

        evt = bc.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)

    def test_bubble_up(self):
        parent = bc.Component('parent')
        mid = middleware.Middleware()
        child = bc.Component('child')

        child2 = bc.Component('child2')
        child2.add_event_listener(bc.Event, 'handle_event')
        child2.handle_event = MagicMock(name='child2.handle_event')

        parent.add_component(mid)
        mid.add_child(child)
        mid.add_child(child2)

        # third party top leve component looking for some sweet
        # Event action
        third_party = bc.Component('third_party')
        third_party.add_event_listener(bc.Event, 'handle_event')
        third_party.handle_event = MagicMock('third_party.handle_event')
        parent.add_component(third_party)

        evt = bc.Event()
        child.broadcast(evt)
        third_party.handle_event.assert_called_once_with(evt)
        # 02-03-13 Problem was that I was using mid.router for
        # bubbling up. So handle_event was called twice, once by the mid.router
        # and again by the parent.router
        child2.handle_event.assert_called_once_with(evt)

parent = bc.Component('parent')
mid = middleware.Middleware()
child = bc.Component('child')

# setup child with series and event bindings
child.add_event_listener(bc.Event, 'handle_event')
child.handle_event = MagicMock()
child.add_series_binding(testing.TestEventA.class_series(), 'handle_series')
child.handle_series = MagicMock()

mid.add_child(child)
parent.add_component(mid)

evt = bc.Event()
parent.broadcast(evt)

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
