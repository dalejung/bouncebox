"""
    This module deals with dispatching / Queue
"""
from collections import deque

from bouncebox.core.errors import DispatcherNotFound

import itertools

class BaseRouter(object):
    """
    This class servers as a router
    This will only work for a single threaded app atm because of 
    self.processing?
    """

    def __init__(self):
        self.backends = []
        self.backend_funcs = []
        self.queue = deque()
        self.processing = 0

    def send(self, message):
        if not self.processing:
            self._process(message)        
        else:
            self.queue.append(message)

    def send_to_backends(self, message):
        for func in self.backend_funcs:
            func(message)

    def _process(self, message=None):
        """
        Try to process next in queue
        """
        self.processing = True
        while True:
            if not message:
                message = self.queue.popleft()
            self.send_to_backends(message)
            message = None
            if len(self.queue) <= 0:
                break
        self.processing = False

    def add_backend(self, backend):
        self.backends.append(backend)
        self.backend_funcs.append(backend.send)

    def bind(self, key, callback, exchange):
        pass

def instance_check(message, key):
    if isinstance(message, key):
        return True

class TERouter(BaseRouter):
    """
    TradeExpression specific router
    Changes made for speed
    """
    def __init__(self):
        """docstring for init"""
        super(TERouter, self).__init__()

        event_dispatcher = EventDispatcher()
        self.event_dispatcher = event_dispatcher
        self.add_backend(event_dispatcher)

        series_dispatcher = SeriesDispatcher()
        self.series_dispatcher = series_dispatcher
        self.add_backend(series_dispatcher)

    def bind(self, key, callback, exchange):
        try:
            attr = exchange + '_dispatcher'
            dispatcher = getattr(self, attr)
            dispatcher.bind(key, callback)
        except AttributeError as err:
            raise DispatcherNotFound(str(err))

    def send(self, message):
        if not self.processing:
            self.processing = True
            while True:
                if not message:
                    message = self.queue.popleft()

                # send_to_backends
                self.event_dispatcher.send(message)
                self.series_dispatcher.send(message)

                message = None
                if len(self.queue) <= 0:
                    break

            self.processing = False
        else:
            self.queue.append(message)


Router = TERouter

class Dispatcher(object):
    """
    Dispatch messages based on message type
    Mainly based off of ListeningElement with certain extra stuff removed
    """
    def __init__(self, key_check):
        super(Dispatcher, self).__init__()
        self.key_check = key_check
        self.callback_registry = {}
        self.send = self.fire_callbacks
        
    def bind(self, key, callback):
        """
        Register a listener
        """
        lst = self.callback_registry.setdefault(key, [])
        lst.append(callback)

    def send(self, message):
        """
            Starting to think that the object itself should
            parcel out its message handlers instead of the bubble
        """
        self.fire_callbacks(message)

    def fire_callbacks(self, message):
        """
            split out to let proxy registries easier  
        """
        registry = self.callback_registry
        for key in registry:
            if self.key_check(message, key):
                callbacks = registry[key]
                for callback in callbacks:
                    callback(message)


class EventDispatcher(Dispatcher):
    """ Optimized for event dispatching """
    def __init__(self):
        super(EventDispatcher, self).__init__(None)
        self.cache_callback_registry = {}

    def fire_callbacks(self, message):
        """
            split out to let proxy registries easier  
        """
        registry = self.cache_callback_registry
        event_type = type(message)
        try:
            callbacks = registry[event_type]
        except:
            registry[event_type] = self.get_callbacks(message)
            callbacks = registry[event_type]

        for callback in callbacks:
            callback(message)

    def get_callbacks(self, message):
        """
        Will take an eventtype and generate all the callbacks for it. Remember,
        callback registry only has callbacks for only that event_type but not
        it's ancestors. So they won't always be the same
        """
        registry = self.callback_registry
        registries = [registry[event_type] for event_type in registry if isinstance(message, event_type)]
        callbacks = list(itertools.chain(*registries))
        return callbacks

class SeriesDispatcher(Dispatcher):
    """
    Dispatch messages based on message type
    Mainly based off of ListeningElement with certain extra stuff removed
    """
    def __init__(self):
        super(SeriesDispatcher, self).__init__(None)
        self.callback_registry = {}
        
    def bind(self, key, callback):
        """
        Register a listener
        """
        lst = self.callback_registry.setdefault(hash(key), [])
        lst.append(callback)

    def send(self, message):
        """
            Starting to think that the object itself should
            parcel out its message handlers instead of the bubble
        """
        self.fire_callbacks(message)

    def fire_callbacks(self, message):
        """
            split out to let proxy registries easier  
        """
        registry = self.callback_registry
        key = message.series._hash
        # hash is slower
        #key = hash(message.series)
        try:
            callbacks = registry[key]
        except:
            registry[key] = []
            callbacks = registry[key]

        for callback in callbacks:
            callback(message)

