"""
    Set of tools to translate between a list of homogenous events and DataFrames
"""
import pandas as pd

def eventlist_to_frame(lst):
    if len(lst) == 0:
        return None

    test = lst[0]
    attrs = test.repr_attrs
    data = []
    for evt in lst:
        l = [getattr(evt, attr) for attr in attrs]
        data.append(l)

    return pd.DataFrame(data, columns=attrs)

class EventList(list):
    _cache_df = None

    def to_frame(self):
        if self._cache_df is None:
            self._cache_df = eventlist_to_frame(self)
        return self._cache_df

    mutation_methods = [
        'append', 
        '__setitem__', 
        '__delitem__',
        'sort', 
        'extend',
        'insert',
        'pop',
        'remove',
        'reverse',
    ]

# alter mutation methods to clear the cached_df
def _binder(method):
    def _method(self, *args, **kwargs):
        self._cache_df = None
        sup = super(EventList, self)
        getattr(sup, method)(*args, **kwargs)
    return _method

for method in EventList.mutation_methods:
    setattr(EventList, method, _binder(method))
