class magicdictset(dict):
    """Helper class to add conveniences to dict."""

    def __getitem__(self, key):
        """Extend getitem behavior to create if not found."""
        if key not in self:
            dict.__setitem__(self, key, set())
        return dict.__getitem__(self, key)

    def updateunion(self, other):
        """Update values using set union."""
        for key in other:
            try:
                my_set = dict.__getitem__(self, key)
                other_set = dict.__getitem__(other, key)
                my_set = my_set.union(other_set)
                dict.__setitem__(self, key, my_set)
            except KeyError:
                other_set = dict.__getitem__(other, key)
                dict.__setitem__(self, key, other_set)
