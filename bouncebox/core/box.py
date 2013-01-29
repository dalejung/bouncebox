from bouncebox.core.component import Component
from bouncebox.core.errors import EndOfSources
from bouncebox.core.event import EndEvent

__all__ = ['BounceBox']

class BounceBox(Component):
    """
        This class contains everything
    """
    def __init__(self):
        super(BounceBox, self).__init__()
        self.sources = []

    def start_box(self, mode='auto', interactive=False):
        """
            Starts the bounce box and calls start on the sources
        """
        if len(self.sources) == 0:
           print "No Sources Attached. Exiting..."
           return
        if interactive:
            self.start_interactive()
        elif mode == 'auto':
            self.start_auto()

    def start_auto(self):
        while True:
            try:
                self.send_next()
            except EndOfSources:
                print 'Done Running Sources'
                break

    def start_interactive(self):
        print """ Interactive Mode 
            Press Enter for one iteration
            Press a number for that many iterations
            Type stop to end session"""
        while True:
            key = raw_input('\nNext ')
            if key == 'stop':
                break
            if key is '':
                key = 1
            try:
                key = int(key)
            except:
                print 'Input is wrong'
                continue
            for x in range(key):
                self.send_next()

    def send_next(self):
        """ Grab next event and send it """
        event = next(self)
        self.send(event)
        return event

    def sender_iter(self):
        """ Returns an iterator that will return """
        while 1:
            yield self.send_next()

    def next(self):
        """
            Out of multiple sources this will send the next
            of chronological order
        """
        #TODO right now this doesn't do the chronological sort
        # currently only supports one source
        try:
            for source in self.sources:
                event = next(source)
                return event
        except StopIteration:
            # send End event
            self.end_box()
            raise EndOfSources

    def __iter__(self):
        return self
    
    def end_box(self):
        """
            Let everyone know the box is done
        """
        self.end_hooks.fire(EndEvent())

    def send(self, message):
        self.router.send(message)

    def add_component(self, component):
        if hasattr(component, 'end'):
            self.end_hooks += component.end
        super(BounceBox, self).add_component(component)

    def add_source(self, component):
        self.sources.append(component)
        self.add_component(component)
