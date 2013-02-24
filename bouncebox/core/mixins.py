import bouncebox.core.dispatch as dispatch
import bouncebox.core.event as be

def component_mixin(base, mixin, override=[]):
    """
    Component based mixin. Called mixin for lack of a better term. 

    Parameters
    ----------
    base : Component Class
        Either the BaseComponent or some subclass. If not the BaseComponent, base will require
        its own _init_hooks and listeners so we don't override the BaseComponent's
    mixin : Class
        Class to merge methods into. Without override, only methods that do not clash are added. 
        Mixins are tracked by classname so we don't mix twice due to reload. 
    override : list
        List of attribute names to force setting on base. This is to override existing methods

    Note:
        The mixin.__init__ is called at the end of BaseComponent.__init__. At this point things like
        add_component_hooks, listeners, broadcast_hooks will be available. 
    """
    mixin_name =  mixin.__name__
    _mixins_ = getattr(base, '_mixins_', [])[:] # copy so we don't modify ancestor
    if mixin_name in _mixins_:
        print '{mixin_name} already mixed'.format(mixin_name=mixin_name)
        return False

    _mixins_.append(mixin_name)

    # note the methods in __dict__ are plain functions and not unbound methods
    # they can be safely bound and used without self typecheck
    mdict = mixin.__dict__
    attrs = [(key, attr) for key, attr in mdict.items()
             if key in override or key not in ['listeners'] and not key.startswith('__')]

    if 'listeners' in mdict:
        listeners = mdict['listeners']
        base_listeners = base.listeners[:] # make copy
        base_listeners.extend(listeners)
        setattr(base, 'listeners', base_listeners)

    if '__init__' in mdict:
        init = mdict['__init__'] # grab the non-method
        base_inits = base._init_hooks.copy()
        base_inits += init
        setattr(base, '_init_hooks', base_inits)

    if 'mixin_add_component_hook' in mdict:
        hook = mdict['mixin_add_component_hook'] 
        base_hooks = base.cls_add_component_hooks.copy()
        base_hooks += hook
        setattr(base, 'cls_add_component_hooks', base_hooks)

    mixed = []
    for key, attr in attrs: 
        if not hasattr(base, key) or key in override:
            mixed.append(key)
            setattr(base, key, attr)

    setattr(base, '_mixins_', _mixins_)
    return True

def _get_callbacks(component):
    event_callbacks = component.get_event_callbacks()
    series_bindings = component.get_series_bindings()
    return event_callbacks, series_bindings

class BubbleDownMixin(object):
    """
        Separated out the BubbleDown logic. Essentially this Mixin allows the parent
        Component to pass events from its front.router to selected children. 
    """
    def __init__(self):
        self.child_event_callbacks = {}
        self.child_series_bindings = {}

        self.down_router = dispatch.Router()
        # TODO, make this lazy added based on whether enable_bubble_down is called
        self.add_event_listener(be.Event, 'handle_bubble_down')

    def enable_bubble_down(self, component):
        """
            Adds component to the bubble_down list which means the parent
            will pass on events from its own front router to the component. 
            This in essense acts as if the child component is registered to
            the parent.front.router
        """
        event_callbacks, series_bindings = _get_callbacks(component)
        # keep track of child callbacks
        self.child_event_callbacks[component] = event_callbacks
        self.child_series_bindings[component] = series_bindings

        # bind to the down_router
        for k, callback in event_callbacks:
            self.down_router.bind(k, callback, 'event')
        for k, callback in series_bindings:
            self.down_router.bind(k, callback, 'series')

    def handle_bubble_down(self, event):
        """
            Event Handler for front.router events
        """
        self.down_router.send(event)

    def bubble_down(self, event):
        """
            Takes an event and passes it to the children as if Middleware did 
            not exist.
        """
        self.down_router.send(event)

    def mixin_add_component_hook(self, *args, **kwargs):
        pass

