from unittest import TestCase

import pandas as pd
import trtools.util.testing as tm

import bouncebox.core.api as core
import bouncebox.event_frame as ef

class TestEvent(core.Event):
    repr_attrs = ('timestamp', 'id', 'data')
    def __init__(self, timestamp, id, data, *args, **kwargs):
        self.id = id
        self.data = data
        super(TestEvent, self).__init__(timestamp, *args, **kwargs)

class TestEventFrame(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_to_frame(self):
        """
            Test creating DataFrame and modifying
        """
        ind = pd.date_range(start="2000/1/1", periods=10)

        events = [TestEvent(ind[i], i, len(ind)-i) for i in range(len(ind))]
        el = ef.EventList(events)
        df = el.to_frame()
        assert el._cache_df is df
        assert len(df) == len(events)
        assert df.ix[9]['data'] == el[9].data
        for i, evt in enumerate(el):
            assert evt.data == df.ix[i]['data']
            assert evt.timestamp == df.ix[i]['timestamp']
            assert evt.id == df.ix[i]['id']

        # modify list
        del el[3]
        assert el._cache_df is None
        df = el.to_frame()
        assert el._cache_df is df
        assert len(df) == len(el)
        for i, evt in enumerate(el):
            assert evt.data == df.ix[i]['data']
            assert evt.timestamp == df.ix[i]['timestamp']
            assert evt.id == df.ix[i]['id']

        el.pop()
        el.pop()
        el.pop()
        assert len(el.to_frame()) == 6, "1 del + 3 pops should be 6 left"
        assert el.to_frame().ix[5]['id'] == 6 # note, we took off last 3 and fourth

    def test_attrs(self):
        """
            Test passing in attrs to init
        """
        ind = pd.date_range(start="2000/1/1", periods=10)

        events = [TestEvent(ind[i], i, len(ind)-i) for i in range(len(ind))]
        el = ef.EventList(events, attrs=['id'])
        df = el.to_frame()
        assert len(df.columns) == 1
        assert df.columns[0] == 'id'
        tm.assert_series_equal(df['id'], pd.Series(range(10)))

    def test_repr_col(self):
        """
        Test that repr col works correctly
        """
        ind = pd.date_range(start="2000/1/1", periods=10)

        events = [TestEvent(ind[i], i, len(ind)-i) for i in range(len(ind))]
        el = ef.EventList(events, attrs=['id'], repr_col=True)
        df = el.to_frame()
        for i, evt in enumerate(events):
            assert repr(evt) == df.repr[i]

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
