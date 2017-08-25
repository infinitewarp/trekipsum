import shlex

import mock

from trekipsum import scrape


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


@mock.patch('trekipsum.scrape.STMScraper.parse_script')
def test_parse_movies(mock_parse_script):
    """Test parse_movies attempts parsing expected number of movie scripts."""
    expected_count = 9  # TODO fix 'fc' script and add abrams movies; this should be 10 or 13
    parsed_scripts = scrape.parse_movies()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count


@mock.patch('trekipsum.scrape.STMScraper.parse_script')
def test_parse_tng(mock_parse_script):
    """Test parse_tng attempts parsing expected number of TNG scripts."""
    expected_count = 176  # TODO verify should this actually be 178?
    parsed_scripts = scrape.parse_tng()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count


@mock.patch('trekipsum.scrape.STMScraper.parse_script')
def test_parse_ds9(mock_parse_script):
    """Test parse_ds9 attempts parsing expected number of DS9 scripts."""
    expected_count = 173  # TODO verify should this actually be 176?
    parsed_scripts = scrape.parse_ds9()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count
