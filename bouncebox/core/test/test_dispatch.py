import unittest
from mock import MagicMock

from bouncebox.core.dispatch import Router, Dispatcher, BaseRouter
import bouncebox.core.event as be
import bouncebox.core.event as be

class SourceEvent(be.Event):
    pass

class TestEvent(be.Event):
    pass

class LoggingObj(object):
    def __init__(self, router):
        self.logs = []
        self.router = router
        self.last_sent = None

    def handle_source_event(self, event):
        new_evt = TestEvent(2)
        # since we're in the middle of event propogation
        # router shoudl queue the next send
        self.router.send(new_evt)
        assert len(self.router.queue) == 1
        assert self.router.queue[0] is new_evt
        self.last_send = new_evt

    def handle_event(self, event):
        self.logs.append(event)

class TestBaseRouter(unittest.TestCase):
    def setUp(self):
        pass

    def test_router(self):
        r = Router()
        # test binding
        comp = MagicMock()

        r.bind(SourceEvent, comp.handle_source_event, 'event')
        r.bind(be.Event, comp.handle_event, 'event')

        sevt = SourceEvent()
        r.send(sevt)
        # assert that SourceEvent triggers both handlers
        comp.handle_source_event.assert_called_once_with(sevt)
        comp.handle_event.assert_called_once_with(sevt)

        evt = be.Event()
        r.send(evt)
        # assert be.Event only triggers handle_event
        assert comp.handle_source_event.call_count == 1
        assert comp.handle_event.call_count == 2

    def test_router_queue(self):
        """
            Testing that broadcasting during event propogation gets queued properly
        """
        r = Router()
        # test binding
        logger = LoggingObj(r)
        logger.handle_source_event = MagicMock(side_effect=logger.handle_source_event)
        logger.handle_event = MagicMock(side_effect=logger.handle_event)
        r.bind(SourceEvent, logger.handle_source_event, 'event')
        r.bind(be.Event, logger.handle_event, 'event')

        sevt = SourceEvent()
        r.send(sevt)
        logger.handle_source_event.assert_called_once_with(sevt)
        # called once for SourceEvent and TestEvent
        assert logger.handle_event.call_count == 2
        assert isinstance(logger.logs[1], TestEvent)

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
