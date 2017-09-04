import json
import pickle
import tempfile

import six

from trekipsum.scrape import writers


def test_dictify_dialog():
    """Test _dictify_dialog correctly de-dupes and organizes into dict(list)."""
    dummy_dialog = [
        ('SPORK', 'Illogical.'),
        ('SPORK', 'Fascinating.'),
        ('PIKARD', 'Engage.'),
        ('PIKARD', 'Engage.'),
        ('PIKARD', 'Engage.'),
        ('PIKARD', 'Make it so.'),
        ('PIKARD', 'Engage.'),
        ('SISQO', 'What the hell is going on?'),
    ]
    expected_output = {
        'SPORK': ['Illogical.', 'Fascinating.'],
        'PIKARD': ['Engage.', 'Make it so.'],
        'SISQO': ['What the hell is going on?'],
    }
    result = writers.dictify_dialog(dummy_dialog)
    assert result.keys() == expected_output.keys()
    for key, lines in six.iteritems(expected_output):
        assert len(lines) == len(result[key])
        assert type(result[key]) is list
        assert set(lines) == set(result[key])


def test_write_raw():
    """Test _write_raw correctly writes formatted "raw" contents."""
    dummy_dialog = [
        ('SPORK', 'Illogical.'),
        ('PIKARD', 'Engage.'),
        ('PIKARD', 'Make it so.'),
        ('PIKARD', 'Engage.'),
    ]
    expected_output = 'SPORK:\nIllogical.\n\n' \
                      'PIKARD:\nEngage.\n\n' \
                      'PIKARD:\nMake it so.\n\n' \
                      'PIKARD:\nEngage.\n\n'
    with tempfile.NamedTemporaryFile(mode='w+') as the_file:
        writers.raw(the_file.name, dummy_dialog)
        the_file.seek(0)
        written_contents = the_file.read()
        assert written_contents == expected_output


def test_write_json():
    """Test _write_json correctly writes contents as JSON."""
    dummy_data = {
        'SPORK': ['Illogical'],
        'PIKARD': ['Engage.', 'Make it so.'],
    }

    with tempfile.NamedTemporaryFile(mode='w+') as the_file:
        writers.json(the_file.name, dummy_data)
        the_file.seek(0)
        written_json = json.load(the_file)
        assert written_json == dummy_data


def test_write_pickle():
    """Test _write_pickle correctly writes pickled contents."""
    dummy_data = {
        'SPORK': ['Illogical'],
        'PIKARD': ['Engage.', 'Make it so.'],
    }

    with tempfile.NamedTemporaryFile(mode='w+b') as the_file:
        writers.pickle(the_file.name, dummy_data)
        the_file.seek(0)
        written_pickle = pickle.load(the_file)
        assert written_pickle == dummy_data
