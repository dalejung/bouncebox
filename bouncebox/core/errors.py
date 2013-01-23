class DispatcherNotFound(Exception):
    """ Dispatcher not found. Exchange might be wrong """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class EndOfSources(StopIteration):
    """ All sources for the bouncebox have been run """
    def __init__(self):
        pass
