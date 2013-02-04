from collections import OrderedDict

from bouncebox.util import Object, EventHook
from bouncebox.core.event import Event
from bouncebox.core.dispatch import Router

class Element(Object):
    pass

class PublishingElement(Element):
    """
        >>> pub.subscribe(sub.handle_event)
        >>> pub.publish(Event())
    """
    def __init__(self):
        super(PublishingElement, self).__init__()
        self.pubsub_router = Router()

    # Subscribe/Publish Paradigm
    def subscribe(self, callback, event_cls=None):
        if event_cls is None:
            event_cls = Event
        self.pubsub_router.bind(event_cls, callback, 'event')

    def publish(self, event):
        self.pubsub_router.send(event)
