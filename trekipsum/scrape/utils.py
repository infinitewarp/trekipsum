import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def retriable_session(total=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """Prepare a requests.Session that has automatic retry enabled."""
    retry = Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
