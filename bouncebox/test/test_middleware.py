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
        
        mid.add_child(child)

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

    def test_parent_add(self):
        """
            Test adding mid to parent. Making sure things are setup correct
        """
        parent = bc.Component('parent')
        mid = middleware.Middleware()

        parent.add_component(mid)
        callback = parent.router.event_dispatcher.callback_registry[bc.Event][0] 
        assert callback == mid.handle_bubble_down

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

    def test_add_filter(self):
        mid = middleware.Middleware()
        mid.add_filter(lambda x: x) 
        try:
            # try adding another down filter
            mid.add_filter(lambda x: x) 
        except:
            pass
        else:
            assert False, "Middleware only supports one filter of each type"

    def test_down_filer(self):
        parent = bc.Component('parent')
        mid = middleware.Middleware()
        child = bc.Component('child')

        # dummy filter
        def filter_event(event):
            event.whee = True
            return event

        # setup child with series and event bindings
        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()
        child.add_event_listener(testing.TestEventB, 'handle_eventb')
        child.handle_eventb = MagicMock()
        child.add_series_binding(testing.TestEventA.class_series(), 'handle_series')
        child.handle_series = MagicMock()

        mid.add_filter(filter_event) 
        mid.add_child(child)
        parent.add_component(mid)

        # test that TestEventA gets modified by filter and also goes to both its 
        # handlers like normal
        evt = testing.TestEventA()
        parent.broadcast(evt)
        child.handle_event.assert_called_once_with(evt)
        assert child.handle_event.call_args[0][0].whee 
        child.handle_series.assert_called_once_with(evt)
        assert child.handle_series.call_args[0][0].whee 
        assert not child.handle_eventb.called 

        # Check same for TestEventB
        evt = testing.TestEventB()
        parent.broadcast(evt)
        child.handle_event.assert_called_with(evt)
        assert child.handle_event.call_args[0][0].whee 
        child.handle_eventb.assert_called_once_with(evt)
        assert child.handle_eventb.call_args[0][0].whee 
        assert child.handle_series.called == 1

    def test_filter_up_down(self):
        parent = bc.Component('parent')
        mid = middleware.Middleware()
        child = bc.Component('child')

        # setup child with series and event bindings
        child.add_event_listener(bc.Event, 'handle_event')
        child.handle_event = MagicMock()
        child.add_event_listener(testing.TestEventB, 'handle_eventb')
        child.handle_eventb = MagicMock()
        child.add_series_binding(testing.TestEventA.class_series(), 'handle_series')
        child.handle_series = MagicMock()

        # Essential a logger
        third_party = bc.Component('third_party')
        third_party.add_event_listener(bc.Event, 'handle_event')
        third_party.handle_event = MagicMock('third_party.handle_event')
        parent.add_component(third_party)

        # dummy filter
        def filter_event(event):
            if not hasattr(event, 'whee'):
                event.whee = 0
            event.whee += 1
            return event

        down_filter = MagicMock(wraps=filter_event)
        up_filter = MagicMock(wraps=filter_event)
        mid.add_filter(down_filter) 
        mid.add_filter(up_filter, type='up') 
        mid.add_child(child)
        parent.add_component(mid)

        evt = bc.Event()
        parent.broadcast(evt)
        child.handle_event.assert_called_once_with(evt)
        assert child.handle_event.call_args[0][0].whee  == 1# added by filter_a
        assert down_filter.call_count == 1

        evt = testing.TestEventA()
        child.broadcast(evt)
        child.handle_series.assert_called_once_with(evt)
        assert child.handle_series.call_args[0][0].whee # added by filter_a
        assert up_filter.call_count == 1
        assert down_filter.call_count == 2 # child broadcasts, router sends back down, goes through down filter agan

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
