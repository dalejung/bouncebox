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
      This stores only the callback listening logic
      This element defines what it will listen to. Something 
      has to pass an event into callback_controller. Then the
      ListeningElement will process that event by calling whatever
      listeners it registered to itself. 

      This does not define how to subscribe to events. It came back from
      when I was using event bubbling and all components got all events.

      It merely provides a pathway to process events passed into
      callback_controller
    """
    listeners = []
    def __init__(self):
        super(ListeningElement, self).__init__()
        self.callback_registry = {}
        self.obj_listeners = []

        self.bind_listeners()

    def bind_listeners(self):
        listeners = self.listeners + self.obj_listeners
        for event_cls, func_name in listeners:
            callback = getattr(self, func_name)
            # ListeningElement api
            self.listen(event_cls, callback)

    def listen(self, event_cls, callback, type='all'):
        """
        Listen based off of Event Type
        """
        type_reg = self.callback_registry.setdefault(type, OrderedDict())
        lst = type_reg.setdefault(event_cls, [])
        lst.append(callback)

    def send_message(self, target, event):
        """
          if you pass message to component directly
        """
        target.callback_controller(event)

    def callback_controller(self, event, type='all'):
        callback_registry = self.callback_registry
        self._callback_registry(callback_registry, event, type)

    def _callback_registry(self, callback_registry, event, type):
        """
            split out to let proxy registries easier  
        """
        registry = callback_registry.get(type, {})
        for event_cls in registry:
            if isinstance(event, event_cls):
                funcs = registry[event_cls]
                for func in funcs:
                    func(event)

    def proxy_events_to(self, component):
        """
            Send all events to component
        """
        self.listen(Event, component.callback_controller)



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
