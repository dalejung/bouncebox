import itertools

import bouncebox.core.api as core

def _get_callbacks(component):
    event_callbacks = component.get_event_callbacks()
    series_bindings = component.get_series_bindings()
    return event_callbacks, series_bindings

class Middleware(core.Component):
    """
        Component that does passthrough for it's children. 

        When compo
    """
    def __init__(self):
        super(Middleware, self).__init__()
        self.child_event_callbacks = {}
        self.child_series_bindings = {}
        self.router.bind(core.Event, self.bubble_up, 'event')

    def get_event_callbacks(self):
        return list(itertools.chain(*self.child_event_callbacks.values()))

    def get_series_bindings(self):
        return list(itertools.chain(*self.child_series_bindings.values()))

    def add_child(self, component, overrides=None):
        event_callbacks, series_bindings = _get_callbacks(component)

        self.child_event_callbacks[component] = event_callbacks
        self.child_series_bindings[component] = series_bindings

        # MiddleWare was already added to another component
        # So we have to bind them here
        if self.front != self: 
            for k, callback in event_callbacks:
                self.front.bind(k, callback, 'event')
            for k, callback in series_bindings:
                self.front.bind(k, callback, 'series')

        super(Middleware, self).add_component(component, contained=True)

    def add_component(self, component):
        """
            This should register the child components events. 
            So that events that Middleware doesn't care about pass through
            in **both** directions. 

            A child broadcasting an event should make it to the box.router, unless
            specifically stopped by Middleware
        """
        raise NotImplementedError()

    def bubble_down(self, event):
        """
            Takes an event and passes it to the children as if Middleware did 
            not exist.
        """
        raise NotImplementedError()

    def bubble_up(self, event):
        """
            Take an event from child and buble up to tradebox
        """
        print event
        self.broadcast(event)

if __name__ == '__main__':
    import bouncebox.test.test_middleware
    reload(bouncebox.test.test_middleware)
