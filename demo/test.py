import bouncebox.core.api as bb
import pandas as pd

class TestEventComponent(bb.Component):
    listeners = [(bb.Event, "handle_event")]

    def __init__(self):
        super(TestEventComponent, self).__init__()

        self.sum = 0

    def handle_event(self, event):
        print event

    def end(self, _event):
        print 'THE END'

ind = pd.date_range(start="2000-01-01", freq="D", periods=10)
# create events
events = (bb.Event(ts) for ts in ind)
box = bb.BounceBox()

# add source, EventBroadcaster will broadcast an iterable
source = bb.EventBroadcaster(events)
box.add_source(source)

comp = TestEventComponent()
box.add_component(comp)

box.start_box()
