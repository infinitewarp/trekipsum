import shlex

from trekipsum.scrape import cli

try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_cli_args():
    """Test parse_cli_args for typical CLI arguments."""
    cli_args = shlex.split('. --tng --json foo.json --ds9')
    with mock.patch('argparse._sys.argv', cli_args):
        args = cli.parse_cli_args()
    assert args.no_assets is False
    assert args.speakers is None
    # If specified, limit source data to
    assert args.mov_tos is False
    assert args.mov_tng is False
    assert args.tng is True
    assert args.ds9 is True
    # Additional optional files to write
    assert args.raw is None
    assert args.json == 'foo.json'
    assert args.pickle is None
    assert args.sqlite is None
    # CLI display options
    assert args.progress is False
    assert args.verbose == 0


@mock.patch('trekipsum.scrape.cli.logging')
@mock.patch('trekipsum.scrape.cli.logger')
def test_configure_logging_0(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 0."""
    cli.configure_logging(0)
    mock_logger.setLevel.assert_called_with(mock_logging.WARNING)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.WARNING,
                                                format=cli.LOG_FORMAT_BASIC)


@mock.patch('trekipsum.scrape.cli.logging')
@mock.patch('trekipsum.scrape.cli.logger')
def test_configure_logging_1(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 1."""
    cli.configure_logging(1)
    mock_logger.setLevel.assert_called_with(mock_logging.INFO)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.INFO,
                                                format=cli.LOG_FORMAT_BASIC)


@mock.patch('trekipsum.scrape.cli.logging')
@mock.patch('trekipsum.scrape.cli.logger')
def test_configure_logging_2(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 2."""
    cli.configure_logging(2)
    mock_logger.setLevel.assert_called_with(mock_logging.DEBUG)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.DEBUG,
                                                format=cli.LOG_FORMAT_NOISY)
