from unittest import TestCase

from mock import MagicMock

import bouncebox.core.component as bc
import bouncebox.core.event as be
import bouncebox.util.testing as testing

class TestPublishing(TestCase):

    def setUp(self):
        pass

    def test_subscribe_event_none(self):
        c1 = bc.Component()
        c2 = bc.Component()
        c2.event_handler = MagicMock()
        c1.subscribe(c2.event_handler)

        evt = be.Event()
        c1.publish(evt)
        c2.event_handler.assert_called_once_with(evt)

        evt = testing.TestEventA()
        c1.publish(evt)
        c2.event_handler.assert_called_with(evt)

    def test_subscribe_specific_event(self):
        c1 = bc.Component()
        c2 = bc.Component()
        c2.event_handler = MagicMock()
        c1.subscribe(c2.event_handler, testing.TestEventB) # bind event class

        evt = testing.TestEventA()
        c1.publish(evt)
        assert not c2.event_handler.called # no match

        evt = testing.TestEventB()
        c1.publish(evt)
        c2.event_handler.assert_called_with(evt)

    def test_publish(self):
        c1 = bc.Component()
        c2 = bc.Component()
        c2.event_handler = MagicMock()
        c1.subscribe(c2.event_handler)

        c2.add_event_listener(be.Event, 'handle_all_events')
        c2.handle_all_events = MagicMock()

        # make sure publish doesn't do regular broadcasting
        c1.add_component(c2)

        evt = testing.TestEventA()
        c1.publish(evt)
        c2.event_handler.assert_called_once_with(evt)

        assert c2.handle_all_events.call_count == 0

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
