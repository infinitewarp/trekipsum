from trekipsum.scrape import magicdictset


def test_magicdictset_getitem_add():
    """Test magicdictset.getitem automagically creates a set."""
    d = magicdictset()
    d['key'].add('thing 1')
    d['key'].add('thing 2')
    d['key'].add('thing 2')  # second time to ensure set behavior

    assert len(d) == 1
    assert 'key' in d
    assert len(d['key']) == 2
    assert 'thing 1' in d['key']
    assert 'thing 2' in d['key']


def test_magicdictset_updateunion():
    """Test magicdictset.updateunion correctly merges another magicdictset."""
    d1 = magicdictset()
    d2 = magicdictset()

    d1['key1'].add('1 hello')
    d1['key1'].add('1 world')
    d1['key2'].add('2 hola')

    d2['key1'].add('1 goodbye')
    d2['key2'].add('2 hola')
    d2['key3'].add('3 adios')

    d1.updateunion(d2)
    assert len(d1) == 3
    assert 'key1' in d1
    assert 'key2' in d1
    assert 'key3' in d1

    assert len(d1['key1']) == 3
    assert '1 hello' in d1['key1']
    assert '1 world' in d1['key1']
    assert '1 goodbye' in d1['key1']

    assert len(d1['key2']) == 1
    assert '2 hola' in d1['key2']

    assert len(d1['key3']) == 1
    assert '3 adios' in d1['key3']
