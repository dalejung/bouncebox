from datetime import datetime
from functools import partial

from bouncebox.util import Object
from  bouncebox.core.series import create_series

class Event(Object):
    repr_attrs = ['timestamp']
    _class_series = None

    # check __setattr__ immutable == True means immutable
    immutable = False

    def __init__(self, timestamp=None, source_event=None, series=None):
        self.generated = datetime.now()
        self.source_event = source_event
        if timestamp is None and source_event:
            timestamp = source_event.timestamp
        self.timestamp = timestamp

        if series is None:
            series = self.__class__.class_series()
        self.series = series
        self.immutable = True

    @classmethod
    def class_series(self):
        # quick way to get default series
        if self._class_series is None:
            self._class_series = create_series(self)
        return self._class_series

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

class EndEvent(Event):
    graphable = False 

class StartEvent(Event):
    """
        Used to signal to bouncebox that it is beginning. 
    """
    graphable = False 

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

class SeriesEventFactory(EventFactory):
    """
        Takes in a Series object and generates events based of those
    """
    def __init__(self, series):
        self.series = series
        self.event_cls = series.event_cls
        self.event_args = series.event_args
        self.create_event_func()
        super(SeriesEventFactory, self).__init__(series.event_cls)

    def create_event_func(self):
        kw = {}
        kw['series'] = self.series
        for arg in self.event_args:
            kw[arg] = getattr(self.series, arg)
        func = partial(self._build_event, **kw)
        self.build_event = func

    def _build_event(self, *args, **kwargs):
        event = self.event_cls(*args, **kwargs)
        return event
