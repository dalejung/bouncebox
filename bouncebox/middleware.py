import itertools

import bouncebox.core.api as core

def _get_callbacks(component):
    event_callbacks = component.get_event_callbacks()
    series_bindings = component.get_series_bindings()
    return event_callbacks, series_bindings

class Middleware(core.Component):
    listeners = [(core.Event, 'handle_bubble_down')]
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

        self.down_router = core.Router()

        self.down_filter = None
        self.up_filter = None
        # TODO support multi filters
        #self.up_filters = []
        #self.down_filters = []

    def add_child(self, component):
        """
           Parameters
           ----------
           component : Component
        """
        # we bubble up or rebroadcast child broadcasts
        component.broadcast = self.handle_bubble_up
        self._init_bubble_down(component)
        self.children.append(component)

    def _init_bubble_down(self, component):
        event_callbacks, series_bindings = _get_callbacks(component)
        # keep track of child callbacks
        self.child_event_callbacks[component] = event_callbacks
        self.child_series_bindings[component] = series_bindings

        # bind to the down_router
        for k, callback in event_callbacks:
            self.down_router.bind(k, callback, 'event')
        for k, callback in series_bindings:
            self.down_router.bind(k, callback, 'series')

    def add_component(self, component, *args, **kwargs):
        """
            see: add_child
        """
        raise NotImplementedError()

    def add_filter(self, filter, type='down', key=None):
        # Eventually I'd want to have a router like system here.
        # but for simplicity, I will have only up/down filter
        if type == 'down':
            if self.down_filter is not None:
                raise Exception("Middleware currently only supports one up and one down filter")
            self.down_filter = filter
            #self.down_filters.append((key, filter))
        else:
            if self.up_filter is not None:
                raise Exception("Middleware currently only supports one up and one down filter")
            self.up_filter = filter
            #self.up_filters.append((key, filter))

    def handle_bubble_down(self, event):
        """
            Event Handler for front.router events
        """
        if self.down_filter:
            event = self.down_filter(event)
        self.bubble_down(event)

    def bubble_down(self, event):
        """
            Takes an event and passes it to the children as if Middleware did 
            not exist.
        """
        self.down_router.send(event)

    def handle_bubble_up(self, event):
        """
            Handle broadcasted events from children and rebroadcast
        """
        if self.up_filter:
            event = self.up_filter(event)
        self.broadcast(event)

if __name__ == '__main__':
    import bouncebox.test.test_middleware
    reload(bouncebox.test.test_middleware)
