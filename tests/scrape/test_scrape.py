import json
import pickle
import shlex
import tempfile

import six

from trekipsum import scrape

try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_cli_args():
    """Test parse_cli_args for typical CLI arguments."""
    cli_args = shlex.split('. --tng -j foo.json --ds9')
    with mock.patch('argparse._sys.argv', cli_args):
        args = scrape.parse_cli_args()
    assert args.all is False
    assert args.movies is False
    assert args.tng is True
    assert args.ds9 is True
    assert args.json == 'foo.json'
    assert args.pickle is None


@mock.patch('trekipsum.scrape.STMScraper.extract_dialog')
def test_parse_movies(mock_extract_dialog):
    """Test parse_movies attempts parsing expected number of movie scripts."""
    expected_count = 9  # TODO fix 'fc' script and add abrams movies; this should be 10 or 13
    dummy_dialog = ('SPORK', 'Fascinating.')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = scrape.parse_movies()
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count


@mock.patch('trekipsum.scrape.STMScraper.extract_dialog')
def test_parse_tng(mock_extract_dialog):
    """Test parse_tng attempts parsing expected number of TNG scripts."""
    expected_count = 176  # TODO verify should this actually be 178?
    dummy_dialog = ('PIKARD', 'Make it so.')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = scrape.parse_tng()
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count


@mock.patch('trekipsum.scrape.STMScraper.extract_dialog')
def test_parse_ds9(mock_extract_dialog):
    """Test parse_ds9 attempts parsing expected number of DS9 scripts."""
    expected_count = 173  # TODO verify should this actually be 176?
    dummy_dialog = ('SISQO', 'What the hell is going on?')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = scrape.parse_ds9()
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count


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
    result = scrape._dictify_dialog(dummy_dialog)
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
        scrape._write_raw(the_file.name, dummy_dialog)
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
        scrape._write_json(the_file.name, dummy_data)
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
        scrape._write_pickle(the_file.name, dummy_data)
        the_file.seek(0)
        written_pickle = pickle.load(the_file)
        assert written_pickle == dummy_data


@mock.patch('trekipsum.scrape.logging')
@mock.patch('trekipsum.scrape.logger')
def test_configure_logging_0(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 0."""
    scrape.configure_logging(0)
    mock_logger.setLevel.assert_called_with(mock_logging.WARNING)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.WARNING,
                                                format=scrape.LOG_FORMAT_BASIC)


@mock.patch('trekipsum.scrape.logging')
@mock.patch('trekipsum.scrape.logger')
def test_configure_logging_1(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 1."""
    scrape.configure_logging(1)
    mock_logger.setLevel.assert_called_with(mock_logging.INFO)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.INFO,
                                                format=scrape.LOG_FORMAT_BASIC)


@mock.patch('trekipsum.scrape.logging')
@mock.patch('trekipsum.scrape.logger')
def test_configure_logging_2(mock_logger, mock_logging):
    """Test configure_logging sets logging for verbosity 2."""
    scrape.configure_logging(2)
    mock_logger.setLevel.assert_called_with(mock_logging.DEBUG)
    mock_logging.basicConfig.assert_called_with(level=mock_logging.DEBUG,
                                                format=scrape.LOG_FORMAT_NOISY)
