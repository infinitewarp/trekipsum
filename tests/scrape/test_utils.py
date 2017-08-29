from trekipsum.scrape.utils import magicdictlist, retriable_session


def test_magicdictlist_getitem():
    """Test magicdictset.getitem automagically creates a list for new keys."""
    d = magicdictlist()
    d['key'].append('thing 1')
    d['key'].append('thing 2')
    d['key'].append('thing 2')

    assert len(d) == 1
    assert 'key' in d
    assert len(d['key']) == 3
    assert 'thing 1' in d['key']
    assert 'thing 2' in d['key']


def test_magicdictlist_dedupe():
    """Test magicdictlist.dedupe correctly returns a de-duplicated magicdictlist."""
    d1 = magicdictlist()

    d1['key1'].append('1 hello')
    d1['key1'].append('1 world')
    d1['key2'].append('2 hello')
    d1['key1'].append('1 world')

    d2 = d1.dedupe()
    assert len(d2) == 2
    assert len(d2['key1']) == 2
    assert len(d2['key2']) == 1
    assert set(d2['key1']) == set(['1 hello', '1 world'])
    assert d2['key2'] == ['2 hello']


def test_retriable_session():
    """Test retriable_session returns a well-constructed requests.Session."""
    total = 5
    backoff_factor = 0.5
    session = retriable_session(total, backoff_factor)
    assert len(session.adapters) == 2
    assert 'https://' in session.adapters
    assert 'http://' in session.adapters
    assert session.adapters['https://'] == session.adapters['http://']
    assert session.adapters['https://'].max_retries.total == total
    assert session.adapters['https://'].max_retries.backoff_factor == backoff_factor
