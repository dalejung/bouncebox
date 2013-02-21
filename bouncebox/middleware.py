from bouncebox.util import EventHook
import bouncebox.core.api as core
from bouncebox.core.mixins import BubbleDownMixin

class MiddlewareMixin(BubbleDownMixin):
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
        self.children = []

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
        self.add_bubble_down(component)
        self.children.append(component)

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


    def handle_bubble_up(self, event):
        """
            Handle broadcasted events from children and rebroadcast
        """
        if self.up_filter:
            event = self.up_filter(event)
        self.broadcast(event)


class Middleware(core.Component):
    # make sure our mixin only affects this specific class
    _init_hooks = EventHook()
    listeners = []
    def __init__(self, *args, **kwargs):
        super(Middleware, self).__init__(*args, **kwargs)

core.component_mixin(Middleware, BubbleDownMixin)
core.component_mixin(Middleware, MiddlewareMixin, override=['add_component', 'handle_bubble_down'])
