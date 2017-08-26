class magicdictlist(dict):
    """Helper class to add conveniences to dict."""

    def __getitem__(self, key):
        """Extend getitem behavior to create if not found."""
        if key not in self:
            dict.__setitem__(self, key, list())
        return dict.__getitem__(self, key)

    def dedupe(self):
        """Return new magicdictlist with de-duplicated lists."""
        newdictlist = magicdictlist()
        for key in self.keys():
            newdictlist[key] = list(set(dict.__getitem__(self, key)))
        return newdictlist
