import shlex

from six import StringIO

from trekipsum import cli

try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_cli_args():
    """Test parse_cli_args for typical CLI arguments."""
    cli_args = shlex.split('. --speaker pikard --no-attribute')
    with mock.patch('argparse._sys.argv', cli_args):
        args = cli.parse_cli_args()
    assert args.speaker == 'pikard'
    assert args.count == 1
    assert args.no_attribute is True
    assert args.debug is False


@mock.patch('sys.stdout', new_callable=StringIO)
def test_print_dialog_with_speaker(mock_stdout):
    """Test print_dialog behavior when show_speaker is True."""
    line, speaker, show = 'Did he say, "engage"?', 'DORF', True
    cli.print_dialog(line, speaker, show)
    assert mock_stdout.getvalue() == '\'Did he say, "engage"?\' -- Dorf\n'


@mock.patch('trekipsum.cli.print')
def test_print_dialog_without_speaker(mock_print):
    """Test print_dialog behavior when show_speaker is False."""
    line, speaker, show = 'Did he say, "engage"?', 'DORF', False
    cli.print_dialog(line, speaker, show)
    mock_print.assert_called_with('\'Did he say, "engage"?\'')
