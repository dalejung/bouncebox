"""
Series Notes:
    A series should be hashable. Once a series is created it shouldn't
    need to be changed and thus immutable in a way.

    So a Series for the 3 length MA of AAPL 1 MIN bars should always
    hash to the same value/id.
"""
#TODO Series hash isn't crossplatform atm. per computer it is
# the same but not guaranteed if we were to start networking
from bouncebox.util import base_repr   
from bouncebox.util import generate_id

class EventSeries(object):
    """
        EventSeries are a series of events. 
        Basically what ties events together into groups
    """
    event_cls = None
    # series args that get passed into build_event
    event_args = []
    # used for printing and equivalance testing
    repr_attrs = []
    # is this a uniform timeseries (ie no gaps)
    uniform = False
    def __init__(self, event_cls=None, label_name=None):
        self.gen_id = generate_id(self)
        self.label_name = label_name
        self._hash = None
        if event_cls:
            self.event_cls = event_cls
        self.generate_hash()

    def __repr__(self):
        return base_repr(self, self.repr_attrs)

    def __str__(self):
        return self.label_name or repr(self)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._hash

    def generate_hash(self):
        repr_attrs = self.repr_attrs 
        if self.label_name:
            repr_attrs += 'label_name'
        attrs = tuple([getattr(self, name) for name in repr_attrs])
        self._hash = hash(attrs)

class TimeSeries(EventSeries):
    """
        Series made up of time intervals. duh classic time series
    """
    uniform = True

def create_series(event_cls):
    series = EventSeries()
    series.event_cls = event_cls
    series.label_name = event_cls.__name__ + ' series(auto)'
    return series
