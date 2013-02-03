from bouncebox.util import Object, EventHook
from bouncebox.core.event import Event

from collections import OrderedDict

class Element(Object):
    def __init__(self):
        self.broadcast_hooks = EventHook()

    def broadcast(self, event):
        self.broadcast_hooks.fire(event)

class ListeningElement(Element):
    """
    """
    listeners = []
    def __init__(self):
        super(ListeningElement, self).__init__()
        self.obj_listeners = []

class PublishingElement(ListeningElement):
    """
        Really this should use the Router of each component
    """
    def __init__(self):
        super(PublishingElement, self).__init__()
        self.subscriber_registry = {}

    # Subscribe/Publish Paradigm
    def subscribe(self, callback, event_cls=None):
        lst = self.subscriber_registry.setdefault(event_cls, [])
        lst.append(callback)

    def publish(self, event):
        registry = self.subscriber_registry
        for event_cls in registry:
            if event_cls is None or isinstance(event, event_cls):
                funcs = registry[event_cls]
                for func in funcs:
                    func(event)
