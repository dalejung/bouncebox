"""
    Tools to help use array like iterables with bouncebox. 

    This is opposed to connecting to a live datasource
"""
import bouncebox.core.api as core

class EventBroadcaster(core.Component):
    """
        Will wrap an iter that returns events.
        This will let us broadcast it
    """
    def __init__(self, source):
        self.iter = iter(source)
        super(EventBroadcaster, self).__init__()

    def start(self, _event=None):
        while self.send_next():
            pass

    def send_next(self):
        """
        send next should never be overriden. 
        always ensure that the event broadcasted 
        is the same as next()
        """
        try:
            event = next(self)
            self.broadcast(event)
            return event
        except StopIteration:
            return False

    def __next__(self):
        """ Iterator Interface"""
        event = next(self.iter)
        return event

    next = __next__

    def __iter__(self):
        return iter(self.iter)

