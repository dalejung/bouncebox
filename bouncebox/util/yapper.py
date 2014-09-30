import bouncebox.core.api as core

class Yapper(core.Component):
    listeners = [(core.Event, 'handle_events')]
    def __init__(self, prefix=''):
        self.prefix = prefix
        super(Yapper, self).__init__()

    def handle_events(self, event):
        print((self.prefix, event))

class SeriesYapper(core.Component):
    series_bindings = [("series", 'handle_events')]
    def __init__(self, series, prefix=''):
        self.series = series
        self.prefix = prefix
        super(SeriesYapper, self).__init__()

    def handle_events(self, event):
        print((self.prefix, event))

class EventYapper(core.Component):
    listeners = [("event_cls", 'handle_events')]
    def __init__(self, event_cls, prefix=''):
        self.event_cls = event_cls
        self.prefix = prefix
        super(EventYapper, self).__init__()

    def handle_events(self, event):
        print((self.prefix, event))
