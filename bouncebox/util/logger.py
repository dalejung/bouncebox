from collections import deque

import bouncebox.core.component as component
import bouncebox.core.event as event

class Logger(component.Component):

    def __init__(self, length=None, series=[], event_types=[event.Event]):
        super(Logger, self).__init__()

        self.length = length
        self.series = series
        self.event_types = event_types
        self.data = {}
        self.all_events = []

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
        lst = self.data.setdefault(key, [])
        lst.append(event)
        self.all_events.append(event)

class MiddleLogger(Logger):

    def __init__(self):
        super(MiddleLogger, self).__init__(None, [], [])

    def log_component(self, component):
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
