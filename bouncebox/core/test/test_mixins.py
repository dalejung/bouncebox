import sys
from unittest import TestCase

from mock import MagicMock

import bouncebox.core.component as bc
import bouncebox.core.event as be
import bouncebox.core.mixins as mixins

class TestBubbleDown(bc.PreMixComponent):
    pass

mixins.component_mixin(TestBubbleDown, mixins.BubbleDownMixin)

class TestBubbleDownMixin(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_bubble_down(self):
        parent = TestBubbleDown()
        mid = TestBubbleDown()
        child = TestBubbleDown()

        child.add_event_listener(be.Event, 'handle_event')
        child.handle_event = MagicMock()

        # We have an order issue
        parent.add_component(mid)
        mid.add_component(child, contained=True)
        mid.enable_bubble_down(child)

        evt = be.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)
