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
from bouncebox.array import EventBroadcaster

def _date_array(arr):
    if arr.dtype.type == np.datetime64:
        return True
    return False

class DateMatcher(object):
    """
        param
        dates: Ordered array of dates. Can repeat. 
        callback: called when next date match occurs
    """
    def __init__(self, dates, callback):
        if not _date_array(dates):
            raise Exception("dates must be DatetimeIndex")
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
        Parameters
        ----------
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

        if not _date_array(dates):
            raise Exception("dates must be DatetimeIndex")

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

    def check_date(self, date):
        return self.dr.check_date(date)

    def process_event(self, event):
        date = event.timestamp.date()
        matches = self.check_date(date)
        if matches is None:
            return
        new_evt = self.date_match(matches, event)
        if new_evt is not None:
            return new_evt

    def handle_event(self, event):
        new_evt = self.process_event(event)
        if new_evt:
            self.broadcast(new_evt)

    def date_match(self, matches, event):
        """ Override this function to create new event """
        evt = DateMatchEvent(event.timestamp, matches)
        return evt

class DateMatchEvent(bb.Event):
    """
        Generic date match Event
    """
    def __init__(self, timestamp, matches):
        super(DateMatchEvent, self).__init__(timestamp)
        self.matches = matches
