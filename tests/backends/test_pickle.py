import copy
import pickle
import platform
import tempfile

import pytest
import six

from trekipsum import exceptions
from trekipsum.backends import pickle as ti_pickle

try:
    from unittest import mock
except ImportError:
    import mock


@mock.patch('trekipsum.backends.pickle.DialogChooser.all_dialog', new_callable=mock.PropertyMock)
def test_chooser_dialog_count(mock_all_dialog):
    """Test RandomDialogChooser.dialog_count counts correctly."""
    mock_all_dialog.return_value = {
        'PIKARD': ['Engage.', 'Make it so.'],
        'DORF': ['Aye, sir.'],
    }
    chooser = ti_pickle.DialogChooser()
    assert chooser.dialog_count == 3


def test_chooser_all_dialog_for_specific_speaker():
    """Test RandomDialogChooser.all_dialog correctly limits load to indicated speaker."""
    mock_pickle_content = {
        'PIKARD': ['Engage.', 'Make it so.'],
        'DORF': ['Aye, sir.']
    }
    expected_chooser_dialog = copy.deepcopy(mock_pickle_content)
    del expected_chooser_dialog['DORF']

    with tempfile.NamedTemporaryFile(mode='r+b') as mock_pickle_file:
        pickle.dump(mock_pickle_content, mock_pickle_file)
        mock_pickle_file.seek(0)
        chooser = ti_pickle.DialogChooser(speaker='PIKARD')
        chooser._pickle_path = mock_pickle_file.name
        assert chooser.all_dialog == expected_chooser_dialog


def test_chooser_all_dialog_for_specific_speaker_not_found():
    """Test RandomDialogChooser.all_dialog raises exception if no data found for speaker."""
    with tempfile.NamedTemporaryFile(mode='r+b') as mock_pickle_file:
        pickle.dump({}, mock_pickle_file)
        mock_pickle_file.seek(0)
        chooser = ti_pickle.DialogChooser(speaker='PIKARD')
        chooser._pickle_path = mock_pickle_file.name
        with pytest.raises(exceptions.SpeakerNotFoundException):
            chooser.all_dialog


def is_cpython2():
    """Determine if we are running CPython 2.x."""
    return six.PY2 and platform.python_implementation() == 'CPython'


@mock.patch('trekipsum.backends.pickle.random.randrange')
@mock.patch('trekipsum.backends.pickle.DialogChooser.all_dialog', new_callable=mock.PropertyMock)
@pytest.mark.skipif(is_cpython2(), reason='mock fails to mock random.randrange in py27')
def test_chooser_random_dialog(mock_all_dialog, mock_randrange):
    """Test RandomDialogChooser.random_dialog picks the right item based on randrange."""
    mock_all_dialog.return_value = {
        'WESLEY': ['I am very smart.'],
        'PIKARD': ['Engage.', 'Make it so.'],
        'DORF': ['Aye, sir.'],
    }
    mock_randrange.return_value = 2
    expected_dialog = 'PIKARD', 'Make it so.'
    chooser = ti_pickle.DialogChooser()
    assert chooser.random_dialog() == expected_dialog
