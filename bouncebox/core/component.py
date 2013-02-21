from collections import Iterable
import functools

from bouncebox.core.event import EndEvent
from bouncebox.core.element import PublishingElement
from bouncebox.core.dispatch import Router

from bouncebox.util import generate_id, EventHook

def _get_event_callbacks(component):
    """
        Process the component and return a callback list
    """
    listeners = component.listeners + component.obj_listeners

    callbacks = []
    for event_cls, callback in listeners:
        # event_cls can be string attribute name
        if isinstance(event_cls, str):
            event_cls = getattr(component, event_cls)

        if isinstance(callback, str):
            # string
            callback = getattr(component, callback)

        assert callable(callback)

        callbacks.append((event_cls, callback))
    return callbacks

def _get_series_bindings(component):
    bindings = component.series_bindings + component.obj_series_bindings

    callbacks = []
    for series, callback in bindings:
        series = _get_series(component, series)
        if not callable(callback):
            callback = getattr(component, callback)
        callbacks.append((series, callback))
    return callbacks

class BaseComponent(PublishingElement):
    """
    """
    cls_add_component_hooks = EventHook()
    listeners = []
    _init_hooks = EventHook()

    def __init__(self):
        super(BaseComponent, self).__init__()

        self.obj_listeners = []

        self.gen_id = generate_id(self)

        self.router = Router()
        self._internal_router = Router()

        self.add_component_hooks = EventHook()
        self.components = []

        self.broadcast_hooks = EventHook()
        self.broadcast_hooks += self.publish
        self.broadcast_hooks += self.send

        self.front = self
        self._init_hooks.fire(self)

    def broadcast(self, event):
        self.broadcast_hooks.fire(event)

    def add_component(self, component, contained=False):
        if len(component.components) > 0:
            raise Exception("Added a component that already has sub-components")

        component.front = self.front
        if contained:
            component.front = self

        self.components.append(component)
        self.add_component_hooks.fire(component)
        self.cls_add_component_hooks.fire(component)

        # shortcut for end and start
        end_func = getattr(component, 'end', None)
        if end_func and callable(end_func):        
            self.bind(EndEvent, end_func, 'event')

    # delegate to router
    def bind(self, key, callback, exchange='event'):
        if self.router is None:
            self.router = Router()
        self.router.bind(key, callback, exchange)

    def send(self, message):
        # note that front isn't always a bouncebox
        self.front.router.send(message)

def add_component_hook(func):
    """
        Ideally this decorator will take a method and add it 
        to it's classes cls_add_component_list

        Right now it's just used to visually distinguish the hook
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper

def _get_series(component, series):
    """
        Helper function that'll return the series object
        from it's attr name
    """
    if isinstance(series, str):
        series = getattr(component, series)
    return series

class SeriesComponent(BaseComponent):
    """
    The part of a Component dealing with receiving/providing
    events and series. Specifically the series.
    """
    series_bindings = []
    series_provided = []
    def __init__(self):
        super(SeriesComponent, self).__init__()
        # TODO get rid of the following line and do it
        # via a decorator
        self.obj_series_bindings = []
        self.add_component_hooks += self.bind_series

    @add_component_hook
    def bind_series(self, component, controller=None):
        bindings = component.get_series_bindings()

        if controller is None:
            controller = self

        if hasattr(controller, 'router'):
            controller = getattr(controller, 'router')

        for series, callback in bindings:
            controller.bind(series, callback, 'series')

    def get_series_bindings(self):
        return _get_series_bindings(self)

    def add_series_binding(self, series, callback):
        self.obj_series_bindings.append((series, callback))

    def get_series_provided(self):
        provided = []
        for series in self.series_provided:
            series = self._get_series(series)
            provided.append(series)
        return provided 

class ListeningComponent(SeriesComponent):
    """
        Handles the listeners binding to the Router
    """
    # protected names
    def __init__(self):
        super(ListeningComponent, self).__init__()

        self.add_component_hooks += self.bind_callbacks

    def add_event_listener(self, event_type, callback):
        self.obj_listeners.append((event_type, callback))

    @add_component_hook
    def bind_callbacks(self, component, controller=None):
        """ 
        bind router callbacks. default to using parents
        router, parameterized so we can pass front in 
        """
        if controller is None:
            controller = self

        if hasattr(controller, 'router'):
            controller = getattr(controller, 'router')

        callbacks = component.get_event_callbacks()

        for event_cls, callback in callbacks:
            controller.bind(event_cls, callback, 'event')

    def get_event_callbacks(self):
        return _get_event_callbacks(self)

class Component(ListeningComponent):
    repr_attrs = ['name']
    def __init__(self, name=None, log_broadcast=False):
        self.name = name
        self.log_broadcast = log_broadcast
        self.send_log = []
        self._internal_router_built = False
        super(Component, self).__init__()

    def broadcast(self, event):
        if self.log_broadcast:
            self.send_log.append(event)
        # hardcoded for speed
        self.publish(event)
        self.send(event)
            
    def init_internal_router(self):
        """
            Register the series and event callbacks to the internal router
        """
        router = self._internal_router
        self.bind_series(self, router)
        self.bind_callbacks(self, router)
        self._internal_router_built = True

    def global_event_handler(self, event):
        """
            Universal Event Handler. Utilitizes the internal router

            Parameters
            ----------
            event: Event
                Event to process via the Component's callbacks

            Notes
            -----
            The event_handler should call the same callbacks as BounceBox.broadcast
        """
        # lazy init internal router. Logic is that by the time event_handler is
        # called the listeners should all be added
        if not self._internal_router_built:
            self.init_internal_router()
        self._internal_router.send(event)

class Source(Component):
    def __init__(self):
        super(Source, self).__init__()
