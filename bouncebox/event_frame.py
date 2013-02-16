"""
    Set of tools to translate between a list of events and DataFrames
"""
from trtools.tools.list_frame import ListFrame

class EventList(ListFrame):
    def __init__(self, data=None, attrs=None, repr_col=False, *args, **kwargs):
        super(EventList, self).__init__(data, attrs, repr_col, *args, **kwargs)

    def to_frame(self, attrs=None, repr_col=None):
        """
            Just an override of base ListFrame. 
            The trtools version doesn't have an idea of repr_attrs. 
            Maybe the trtools version needs to make grabbing the object attrs
            an overridable method
        """
        if attrs is None and self.attrs is None:
            test = self[0]
            attrs = test.repr_attrs
        return super(EventList, self).to_frame(attrs, repr_col)
