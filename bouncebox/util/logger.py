from collections import deque

import bouncebox.core.component as component
import bouncebox.core.event as event
from bouncebox.event_frame import EventList

class Logger(component.Component):
    """
        Class to log events sent to it via the box router. It will default to capturing
        all events and storing them separately by EventSeries. Logger.all_events will have all
        events combined in correct order. 

        Paramters
        ---------
        series : list of EventSeries
        event_types : list of classes (default: event.Event)
    """
    def __init__(self, length=None, series=[], event_types=[event.Event]):
        super(Logger, self).__init__()

        self.length = length
        self.series = series
        self.event_types = event_types
        self.data = {}
        self.all_events = EventList(attrs=['timestamp'], repr_col=True)

        self._add_bindings()

    def _add_bindings(self):
        for series in self.series:
            self.add_series_binding(series, self.handle_events)

        for event_type in self.event_types:
            self.add_event_listener(event_type, self.handle_events)

    def handle_events(self, event):
        self.log(event)

    def get_key(self, event):
        try:
            key = event.series 
        except AttributeError:
            key = event.__class__

        return str(key)

    def log(self, event):
        key = self.get_key(event)
        lst = self.data.setdefault(key, EventList())
        lst.append(event)
        self.all_events.append(event)

    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        raise AttributeError()

    def __repr__(self):
        out = []
        out.append(self.__class__.__name__)
        for k, v in self.data.iteritems():
            out.append("{0}: {1} items".format(k, len(v)))
        return '\n'.join(out)

class MiddleLogger(Logger):
    """
        Class for logging only specific components. MiddleLogger will rebroadcast
        the events so it should not affect the box events. 

        Note
        ----

        This will only log the events that the component broadcasts itself. It will not log
        events sent to the component

        Examples
        --------
        >>> box.add_component(logger)
        >>> box.add_component(some_component)
        >>> logger.log_component(some_component)
    """
    def __init__(self):
        super(MiddleLogger, self).__init__(None, [], [])

    def log_component(self, component):
        # replace component's broadcast
        component.broadcast = self.handle_events

    def handle_events(self, event):
        self.log(event)
        # rebroadcast
        self.broadcast(event)

class FileLogger(Logger):
    def __init__(self, length=None, file=None): 
        super(FileLogger, self).__init__(length)
        self.file = file 

    def end(self, _event):
        import cPickle as pickle
        # Get rid of last. It points to components
        for events in self.series.itervalues():
            for evt in events:
                try:
                    del evt.last
                except AttributeError:
                    pass
        data = self.series
        pickle.dump(data, self.file, 2)
        self.file.close()

def install_ipython_completers():  # pragma: no cover
    """Register the DataFrame type with IPython's tab completion machinery, so
    that it knows about accessing column names as attributes."""
    from IPython.utils.generics import complete_object
    from pandas.compat import py3compat

    @complete_object.when_type(Logger)
    def complete_logger(obj, prev_completions):
        return ['all_events'] + [c for c in obj.data.keys() \
                    if isinstance(c, basestring) and py3compat.isidentifier(c)]                                          
# Importing IPython brings in about 200 modules, so we want to avoid it unless
# we're in IPython (when those modules are loaded anyway).
import sys
if "IPython" in sys.modules:  # pragma: no cover
    try: 
        install_ipython_completers()
    except Exception:
        pass 
