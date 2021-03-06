import sys
from unittest import TestCase

from mock import MagicMock

import bouncebox.core.component as bc
import bouncebox.core.event as be

class LoggingChild(bc.BaseComponent):
    def __init__(self):
        self.logs = []
        super(LoggingChild, self).__init__()

    def handle_event(self, event):
        self.logs.append(event)   

class TestEventA(be.Event):
    pass

class TestEventB(be.Event):
    pass

class TestBaseComponent(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_add_component(self):
        """
            
        """
        comp = bc.BaseComponent()
        child = bc.BaseComponent()

        comp.add_component(child)
        assert child in comp.components

    def test_init_hooks(self):
        """
        Test that init_hooks run correctly.
        """
        def init(self):
            self.ran_init = True
            assert isinstance(self, bc.BaseComponent)
            # base component should has these
            assert hasattr(self, 'router')
            assert hasattr(self, 'components')
        bc.BaseComponent._init_hooks += init
        comp = bc.BaseComponent()
        assert comp.ran_init

        # remove handlers
        for handler in bc.BaseComponent._init_hooks:
            bc.BaseComponent._init_hooks.remove_handler(handler)

        assert len(bc.BaseComponent._init_hooks) == 0

    def test_bind(self):
        comp = bc.BaseComponent()
        child = LoggingChild()
        grandchild = LoggingChild()

        # log routers
        child.router.start_logging()
        comp.router.start_logging()

        comp.add_component(child)
        child.add_component(grandchild)

        # test binding
        comp.bind(be.Event, child.handle_event)
        evt = be.Event()
        comp.broadcast(evt)
        assert child.logs[0] is evt

        # grandchild should broadcast to child router and not comp.router
        child.bind(be.Event, child.handle_event) # have child listen to its own router
        evt3 = be.Event()
        grandchild.broadcast(evt3)
        assert child.logs[1] is evt3
        assert child.router.logs[0] is evt3
        assert evt3 not in comp.router.logs

class TestSeriesComponent(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_series_bindings(self):
        """
            Test that series binding works
        """
        parent = bc.SeriesComponent()
        child = bc.SeriesComponent()
        # setup child with series binding via strings
        child.series_bindings = [('sig_a', 'handle_a'), \
                           ('sig_b', 'handle_b')]
        child.sig_a = TestEventA.class_series()
        child.sig_b = TestEventB.class_series()
        child.handle_a = MagicMock()
        child.handle_b = MagicMock()

        bindings = child.get_series_bindings()
        assert len(bindings) == 2

        parent.add_component(child)
        evt_a = TestEventA()
        evt_b = TestEventB()
        parent.broadcast(evt_a)
        parent.broadcast(evt_b)
        child.handle_a.assert_called_once_with(evt_a)
        child.handle_b.assert_called_once_with(evt_b)
        assert child.handle_a.call_count == 1
        assert child.handle_b.call_count == 1

class TestBounceBoxComponent(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_add_component(self):
        parent = bc.Component()
        child = bc.Component()
        # setup child
        child.add_event_listener(TestEventA, 'handle_a')
        child.handle_a = MagicMock()
        child.add_event_listener(TestEventB, 'handle_b')
        child.handle_b = MagicMock()
        child.add_event_listener(TestEventA, 'handle_a2')
        child.handle_a2 = MagicMock()

        child.get_event_callbacks = MagicMock(wraps=child.get_event_callbacks)
        parent.add_component(child)
        # make sure the proper get_event_callbacks is being called
        # 02-03-13 I was having it call the self i.e. parent
        assert child.get_event_callbacks.called
        evt_a = TestEventA()
        parent.broadcast(evt_a)
        assert child.handle_a.called
        assert child.handle_a2.called # test that both TestEventA get called
        assert not child.handle_b.called

        evt_b = TestEventB()
        parent.broadcast(evt_b)
        assert child.handle_a.call_count == 1 # not called 
        assert child.handle_a2.call_count == 1 # not called
        child.handle_b.assert_called_once_with(evt_b)

    def test_process_callbacks(self):
        """
            Test that process_callbacks returns the proper callbacks
        """
        child = bc.Component()
        # setup child
        child.add_event_listener(TestEventA, 'handle_a')
        child.handle_a = MagicMock()
        child.add_event_listener(TestEventB, 'handle_b')
        child.handle_b = MagicMock()
        child.add_event_listener(TestEventA, 'handle_a2')
        child.handle_a2 = MagicMock()

        callbacks = child.get_event_callbacks()
        # Component now has a default bubble_down listener...
        assert len(callbacks) == 4
        for e, c in callbacks:
            if e is TestEventA:
                assert c in [child.handle_a, child.handle_a2]
            else:
                assert c in [child.handle_b, child.handle_bubble_down]

    def test_internal_router(self):
        """
            Test that the internal router works
        """
        child = bc.Component()
        # setup child
        # event type handlers
        child.add_event_listener(TestEventA, 'handle_a')
        child.handle_a = MagicMock()
        child.add_event_listener(TestEventB, 'handle_b')
        child.handle_b = MagicMock()
        child.add_event_listener(TestEventA, 'handle_a2')
        child.handle_a2 = MagicMock()
        # series handlers
        child.series_bindings = [('sig_a', 'handle_a_series'), \
                           ('sig_b', 'handle_b_series')]
        child.sig_a = TestEventA.class_series()
        child.sig_b = TestEventB.class_series()
        child.handle_a_series = MagicMock()
        child.handle_b_series = MagicMock()

        # removed init. should lazy load and work normally
        #child.init_internal_router()

        evt_a = TestEventA()
        child.global_event_handler(evt_a)

        child.handle_a.assert_called_once_with(evt_a)
        assert child.handle_b.call_count == 0
        child.handle_a2.assert_called_once_with(evt_a)
        child.handle_a_series.assert_called_once_with(evt_a)
        assert child.handle_b_series.call_count == 0

        evt_b = TestEventB()
        child.global_event_handler(evt_b)
        assert child.handle_a.call_count == 1 # not called again
        assert child.handle_a2.call_count == 1 # not called again
        child.handle_b.assert_called_once_with(evt_b)
        child.handle_b_series.assert_called_once_with(evt_b)
        child.handle_a_series.call_count == 1

        parent = bc.Component()
        parent.add_component(child)

        # check the callbacks.
        # internal router should be same as front.router
        router = parent.router
        internal_router = child._internal_router

        # dict eq shold be enough
        assert router.event_dispatcher.callback_registry == \
                internal_router.event_dispatcher.callback_registry

        assert router.series_dispatcher.callback_registry == \
                internal_router.series_dispatcher.callback_registry

    def test_send_log(self):
        """
            Test logging broadcasted events
        """
        comp = bc.Component(log_broadcast=True)
        b = be.Event(None)
        comp.broadcast(b)
        c = be.Event(None)
        comp.broadcast(c)
        assert len(comp.send_log) == 2
        assert b == comp.send_log[0]
        assert c == comp.send_log[1]

    def test_add_component_order(self):
        """
        Adding a component that already has sub components is an error.
        The ordering matters because the .front of the sub components is already set. 
        If you add the parent, and then the children, the children will grab the parent's front. 
        So we error if adding a component that is already a parent
        """
        # 02-21-13
        # Because sub components are always contained. It doesn't matter the order.
        # comp.front will always be parent. test is useless
        grandparent = bc.Component()
        parent = bc.Component()
        child = bc.Component()

        # this used to error. Now is fine
        parent.add_component(child) 
        grandparent.add_component(parent)

        grandparent = bc.Component()
        parent = bc.Component()
        child = bc.Component()

        # correct order
        grandparent.add_component(parent)
        parent.add_component(child) 

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
