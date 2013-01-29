from datetime import datetime

from bouncebox.util import Object

class Event(Object):
    repr_attrs = ['timestamp']

    # check __setattr__ immutable == True means immutable
    immutable = False

    def __init__(self, timestamp=None, source_event=None, series=None):
        self.generated = datetime.now()
        self.source_event = source_event
        if timestamp is None and source_event:
            timestamp = source_event.timestamp
        self.timestamp = timestamp
        self.series = series
        self.immutable = True

    def ___setattr__(self, name, value):
        # events are immutable
        if self.immutable:
            assert False, 'boo'
        super(Event, self).__setattr__(name, value) 


# Would like this switchable? Eventually remove non cython version?
try: 
    from bouncebox.core.event_cython import Event
except:
    print 'No cython Event'

class SourceEvent(Event):
    """
        Would like to disintuish events that are generated externally
    """

class EventFactory(object):
    """
        Events should come from some sort of factory. 
        Not sure if factory is the right word. 
        Just a place to keep grouped events metadata together
    """

    def __init__(self, event_cls):
        self.event_cls = event_cls 

    def build_event(self, *args, **kwargs):
        event = self.event_cls(*args, **kwargs)
        event.factory = self
        return event

class EndEvent(Event):
    graphable = False 

class StartEvent(Event):
    """
        Used to signal to bouncebox that it is beginning. 
    """
    graphable = False 
