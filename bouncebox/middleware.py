import itertools

import bouncebox.core.api as core

def _get_callbacks(component):
    event_callbacks = component.get_event_callbacks()
    series_bindings = component.get_series_bindings()
    return event_callbacks, series_bindings

class Middleware(core.Component):
    """
        Component that does passthrough for it's children. 

        Notes
        -----
        This is for getting in between parent and child components. If there are no
        overrides, then the Middleware should habve no effect on the bouncebox.
        Having multiple children should behave the same as having one Middleware
        per child. So 1 Middleware -> Many Children should behave like 1 Middle -> 1 Child.

        This means there is NO sibling behaviors. 

        A usecase may be to alter or prohibit events going to children
    """
    def __init__(self):
        super(Middleware, self).__init__()
        self.child_event_callbacks = {}
        self.child_series_bindings = {}
        self.children = []

    def get_event_callbacks(self):
        return list(itertools.chain(*self.child_event_callbacks.values()))

    def get_series_bindings(self):
        return list(itertools.chain(*self.child_series_bindings.values()))

    def add_child(self, component, overrides=None):
        """
            
        """
        # we bubble up or rebroadcast child broadcasts
        component.broadcast = self.bubble_up

        event_callbacks, series_bindings = _get_callbacks(component)
        # keep track of child callbacks
        self.child_event_callbacks[component] = event_callbacks
        self.child_series_bindings[component] = series_bindings

        # MiddleWare was already added to another component
        # So we have to bind them here
        if self.front != self: 
            for k, callback in event_callbacks:
                self.front.bind(k, callback, 'event')
            for k, callback in series_bindings:
                self.front.bind(k, callback, 'series')

        self.children.append(component)

    def add_component(self, component):
        """
            see: add_child
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
