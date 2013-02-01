"""
    date_responder

    Classes to generate events at specific timestamp. This is useful for preprocessing signals 
    and sending them into the BounceBox.

    >>> signal = series1 > sereis2 + 10
    >>> tr = TransactionResponder(signal)
    >>> box.add_component(tr)


"""
import types

import pandas as pd
import numpy as np

import bouncebox.core.api as bb

class DateMatcher(object):
    """
        param
        dates: Ordered array of dates. Can repeat. 
        callback: called when next date match occurs
    """
    def __init__(self, dates, callback):
        self.dates = dates
        self.callback = callback
        self.current = 0
        self.current_date = self.dates[0]

    def check_date(self, date):
        if self.current_date is None:
            return

        date = pd.Timestamp(date)

        if self.current_date == date:
            matches = np.where(self.dates == date)[0] # get int positions
            self.current += len(matches)
            try:
                self.current_date = self.dates[self.current]
            except:
                self.current_date = None # reached end
            return self.callback(matches)

        if self.current_date < date:
            raise Exception("We skipped ahead into future. Something wrong")

class DateResponder(bb.Component):
    """
        params
        trans: DataFrame of data needed for each date match
        dates: array of dates to key datematch, defaults to trans.index
        values: Do we use the values array? Must faster to stay in numpy land
    """
    def __init__(self, trans, dates=None, event_cls=None, values=False, callback=None):
        super(DateResponder, self).__init__()
        self.trans = trans
        self._init_values(values)

        if dates is None:
            dates = trans.index
        self.dates = dates
        self.dr = DateMatcher(self.dates, self.handle_date_match)

        if callback:
            self.date_match = types.MethodType(callback, self)

        # register Event
        if event_cls:
            self.obj_listeners.append((event_cls, 'handle_event'))

    def _init_values(self, values):
        """
            Grabbing from numpy array is quick since we won't be building DataFrames.
            Leaving it optinoal
        """
        trans = self.trans
        if values:
            self.values = trans.values
            self.handle_date_match = lambda matches: self.values[matches]
        else:
            self.values = trans.reset_index()
            self.handle_date_match = lambda matches: self.values.ix[matches]

    def handle_event(self, event):
        date = event.timestamp.date()
        matches = self.dr.check_date(date)
        if matches is not None:
            self.date_match(matches, event)

    def date_match(self, matches, event):
        evt = DateMatchEvent(event.timestamp, matches)
        self.broadcast(evt)

class DateMatchEvent(bb.Event):
    """
        Generic date match Event
    """
    def __init__(self, timestamp, matches):
        super(DateMatchEvent, self).__init__(timestamp)
        self.matches = matches

if __name__ == '__main__':
    from bouncebox.util.logger import Logger

    ind = pd.date_range(start="2000-01-01", freq="D", periods=20)

    dates = ind[[1,3,7]]
    dates = dates.repeat(3)

    trans = pd.DataFrame({'blah':range(len(dates)), 'high':np.random.randn(len(dates))}, index=dates)

    events = bb.EventBroadcaster([bb.SourceEvent(date) for date in ind])
    box = bb.BounceBox()
    box.add_source(events)

    logger = Logger()
    box.add_component(logger)

    # need an easier way to grab this
    s = bb.create_series(DateMatchEvent)

    def dummy_print(self, matches, event):
        print matches

    tr = DateResponder(trans, values=True, event_cls=bb.SourceEvent, callback=dummy_print)
    box.add_component(tr)

    box.start_box()
    #match_events = logger.data[str(s)]
    #assert len(match_events) == len(dates.unique()) # one match per unique date

