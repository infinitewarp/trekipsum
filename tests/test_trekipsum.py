import copy
import pickle
import platform
import shlex
import tempfile

import pytest
import six
from six import StringIO

import trekipsum

try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_cli_args():
    """Test parse_cli_args for typical CLI arguments."""
    cli_args = shlex.split('. --speaker pikard --no-attribute')
    with mock.patch('argparse._sys.argv', cli_args):
        args = trekipsum.parse_cli_args()
    assert args.speaker == 'pikard'
    assert args.count == 1
    assert args.no_attribute is True
    assert args.debug is False


@mock.patch('sys.stdout', new_callable=StringIO)
def test_print_dialog_with_speaker(mock_stdout):
    """Test print_dialog behavior when show_speaker is True."""
    line, speaker, show = 'Did he say, "engage"?', 'DORF', True
    trekipsum.print_dialog(line, speaker, show)
    assert mock_stdout.getvalue() == '\'Did he say, "engage"?\' -- Dorf\n'


@mock.patch('trekipsum.print')
def test_print_dialog_without_speaker(mock_print):
    """Test print_dialog behavior when show_speaker is False."""
    line, speaker, show = 'Did he say, "engage"?', 'DORF', False
    trekipsum.print_dialog(line, speaker, show)
    mock_print.assert_called_with('\'Did he say, "engage"?\'')


@mock.patch('trekipsum.RandomDialogChooser.all_dialog', new_callable=mock.PropertyMock)
def test_chooser_dialog_count(mock_all_dialog):
    """Test RandomDialogChooser.dialog_count counts correctly."""
    mock_all_dialog.return_value = {
        'PIKARD': ['Engage.', 'Make it so.'],
        'DORF': ['Aye, sir.'],
    }
    chooser = trekipsum.RandomDialogChooser()
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
        chooser = trekipsum.RandomDialogChooser(speaker='PIKARD')
        chooser._pickle_path = mock_pickle_file.name
        assert chooser.all_dialog == expected_chooser_dialog


def test_chooser_all_dialog_for_specific_speaker_not_found():
    """Test RandomDialogChooser.all_dialog raises exception if no data found for speaker."""
    with tempfile.NamedTemporaryFile(mode='r+b') as mock_pickle_file:
        pickle.dump({}, mock_pickle_file)
        mock_pickle_file.seek(0)
        chooser = trekipsum.RandomDialogChooser(speaker='PIKARD')
        chooser._pickle_path = mock_pickle_file.name
        with pytest.raises(trekipsum.SpeakerNotFoundException):
            chooser.all_dialog


def is_cpython2():
    """Determine if we are running CPython 2.x."""
    return six.PY2 and platform.python_implementation() == 'CPython'


@mock.patch('trekipsum.random.randrange')
@mock.patch('trekipsum.RandomDialogChooser.all_dialog', new_callable=mock.PropertyMock)
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
    chooser = trekipsum.RandomDialogChooser()
    assert chooser.random_dialog() == expected_dialog
