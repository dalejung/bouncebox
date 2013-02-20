from trtools.tools.repr_tools import base_repr   

class Object(object):
    repr_attrs = []
    """
    The base object for everything 
    """
    def __repr__(self):
        return base_repr(self, self.repr_attrs)

class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def add_handler(self, handler):
        self.__handlers.append(handler)
        return self

    def remove_handler(self, handler):
        self.__handlers.remove(handler)
        return self

    def __iadd__(self, handler):
        return self.add_handler(handler)

    def __isub__(self, handler):
        return self.remove_handler(handler)

    def fire(self, *args, **kwargs):
        skip = kwargs.pop('skip',None)
        for handler in self.__handlers:
            im_self = getattr(handler, 'im_self', None)
            if im_self and im_self == skip:
                continue
            try:
                handler(*args, **kwargs)
            except:
                raise

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

    def __contains__(self, other):
        return other in self.__handlers

    def __repr__(self):
        return repr(self.__handlers)

import uuid
from itertools import izip
from operator import itemgetter
from collections import namedtuple

def generate_id(obj, instrument=None):
    """
        The general idea behind this is that we create an id
        that is unique to that object but still had some data about
        it. So it would help with logging perhaps
    """
    id = str(obj.__class__.__name__)
    if instrument:
        id += '_'+str(instrument)
    id += '_'+str(uuid.uuid4())
    return id 
