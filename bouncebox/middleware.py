import bouncebox.core.api as core

class Middleware(core.Component):
    """
        Component that does passthrough for it's children. 

        When compo
    """
    def __init__(self):
        super(Middleware, self).__init__()

    def add_child(self, component, overrides=None):
        super(Middleware, self).add_component(component)

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
        raise NotImplementedError()

if __name__ == '__main__':
    import bouncebox.test.test_middleware
    reload(bouncebox.test.test_middleware)
