from unittest import TestCase

import pandas as pd

import bouncebox.util.date_responder as date_responder
from bouncebox.util.date_responder import *
from bouncebox.util.logger import Logger
from bouncebox.array import EventBroadcaster

ind = pd.date_range(start="2000-01-01", freq="D", periods=500)
ind = ind.repeat(3)
dates = ind[ind.dayofweek == 3]
trans = pd.DataFrame({'blah':range(len(dates)), 'high':np.random.randn(len(dates))}, index=dates)

class TestDateResponder(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_date_matcher(self):
        ds = DateMatcher(dates=dates, callback=lambda x: x)
        m = ds.check_date(dates[0])
        assert list(m) == [0,1,2]

        # NOTE: each date repeats to test non-unique
        m = ds.check_date(dates[1]) # already done
        assert m is None

        m = ds.check_date(dates[3]) # next date
        assert list(m) == [3,4,5]

    def test_date_responder(self):
        ind = pd.date_range(start="2000-01-01", freq="D", periods=20)

        dates = ind[[1,3,7]]
        dates = dates.repeat(3)

        trans = pd.DataFrame({'blah':range(len(dates)), 'high':np.random.randn(len(dates))}, index=dates)
        events = EventBroadcaster([bb.SourceEvent(date) for date in ind])
        box = bb.BounceBox()
        box.add_source(events)

        logger = Logger()
        box.add_component(logger)

        # need an easier way to grab this
        s = bb.create_series(DateMatchEvent)

        tr = DateResponder(trans, values=True, event_cls=bb.SourceEvent)
        box.add_component(tr)

        box.start_box()
        match_events = logger.data[str(s)]
        assert len(match_events) == len(dates.unique()) # one match per unique date

if __name__ == '__main__': 
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
