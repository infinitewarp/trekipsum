import os
import tempfile

import six

from trekipsum.scrape import stminutiae

try:
    from unittest import mock
except ImportError:
    import mock

TESTS_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_ASSETS_PATH = os.path.join(TESTS_ROOT_PATH, 'assets')


def extract_speakers(all_dialog):
    """Get set of speakers from the extracted dialog."""
    return set([speaker for speaker, _ in all_dialog])


def extract_lines(all_dialog, speaker):
    """Get only one speaker's lines from the extracted dialog."""
    return [line for line_speaker, line in all_dialog if line_speaker == speaker]


@mock.patch('trekipsum.scrape.stminutiae.retriable_session')
def test_scrape_script(mock_retriable_session):
    """Test scrape_script successfully pulls down and writes data."""
    with open(os.path.join(TEST_ASSETS_PATH, 'tng.txt')) as source_file:
        dummy_script = source_file.read()

    mock_url = 'http://example.foobar/{}.txt'
    script_id = 1701
    expected_called_url = mock_url.format(script_id)
    mock_retriable_session.return_value.get.return_value.text = dummy_script

    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        scraper = stminutiae.Scraper()
        scraper.script_url = mock_url
        scraper.scrape_script(script_id, out_file.name)
        mock_retriable_session.assert_called_with()
        mock_retriable_session.return_value.get.assert_called_with(expected_called_url, timeout=1)

        out_file.seek(0)
        written_contents = out_file.read()
        assert written_contents == dummy_script


@mock.patch('trekipsum.scrape.stminutiae.retriable_session')
def test_scrape_script_not_found(mock_retriable_session):
    """Test scrape_script handles 404 not found when scraping a script."""
    mock_url = 'http://example.foobar/{}.txt'
    script_id = 1702
    expected_called_url = mock_url.format(script_id)

    mock_get = mock_retriable_session.return_value.get
    if six.PY3:
        mock_get.return_value.__bool__.return_value = False
    else:
        mock_get.return_value.__nonzero__.return_value = False
    mock_get.return_value.text = 'This is not the document you are looking for.'
    mock_get.return_value.url = mock_url.format(script_id)
    mock_get.return_value.status_code = 404
    mock_get.return_value.reason = 'not found'

    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        scraper = stminutiae.Scraper()
        scraper.script_url = mock_url
        scraper.scrape_script(script_id, out_file.name)
        out_file.seek(0, 2)  # seeks end of the file
        size = out_file.tell()
        assert size == 0  # file should be empty

    mock_get.assert_called_with(expected_called_url, timeout=1)


def test_parse_script_mock_tng():
    """Test parse_script against dummy TNG-formatted script."""
    scraper = stminutiae.Scraper()
    scraper.assets_path = TEST_ASSETS_PATH
    with mock.patch.object(scraper, 'scrape_script') as mock_scrape_script:
        all_dialog = scraper.extract_dialog('tng')
        assert mock_scrape_script.called is False

    expected_speakers = set(('PIKARD', 'BROI', 'DORF', 'DADA', 'WESLEY', 'Z'))

    assert len(all_dialog) > 0
    assert extract_speakers(all_dialog) == expected_speakers

    parsed_dialog = dict((s, extract_lines(all_dialog, s)) for s in expected_speakers)
    assert len(parsed_dialog['PIKARD']) == 10
    assert len(parsed_dialog['BROI']) == 2
    assert len(parsed_dialog['DORF']) == 1
    assert len(parsed_dialog['DADA']) == 5
    assert len(parsed_dialog['WESLEY']) == 2
    assert len(parsed_dialog['Z']) == 5

    assert 'one two three four five six seven eight nine ten eleven ...' in parsed_dialog['PIKARD']
    assert '... twelve thirteen. fourteen fifteen?' in parsed_dialog['PIKARD']
    assert 'sixteen seventeen' in parsed_dialog['DADA']
    assert 'eighteen' in parsed_dialog['PIKARD']
    assert 'nineteen twenty' in parsed_dialog['BROI']
    assert 'twenty-one' in parsed_dialog['PIKARD']
    assert 'twenty-two' in parsed_dialog['DADA']
    assert 'twenty-three' in parsed_dialog['PIKARD']
    assert 'twenty-four.' in parsed_dialog['DADA']
    assert 'twenty-five ...' in parsed_dialog['PIKARD']
    assert 'twenty-six twenty-seven ...' in parsed_dialog['DADA']
    assert 'twenty-eight ...' in parsed_dialog['PIKARD']
    assert '... twenty-nine thirty ...' in parsed_dialog['DADA']
    assert 'thirty-one thirty-two ...' in parsed_dialog['BROI']
    assert 'thirty-three thirty-four ...' in parsed_dialog['DORF']
    assert 'thirty-five' in parsed_dialog['Z']
    assert 'thirty-six thirty-seven' in parsed_dialog['PIKARD']
    assert 'thirty-eight thirty-nine forty' in parsed_dialog['Z']
    assert 'forty-one' in parsed_dialog['PIKARD']
    assert 'forty-two' in parsed_dialog['Z']
    assert 'forty-three... ! forty-four forty-five' in parsed_dialog['PIKARD']
    assert 'forty-six forty-seven' in parsed_dialog['Z']
    assert 'forty-eight' in parsed_dialog['WESLEY']
    assert 'forty-nine' in parsed_dialog['Z']
    assert 'fifty' in parsed_dialog['WESLEY']


def test_parse_script_mock_tng_weird_space():
    """Test parse_script against dummy TNG-formatted script that has a spacing issue."""
    scraper = stminutiae.Scraper()
    scraper.assets_path = TEST_ASSETS_PATH
    with mock.patch.object(scraper, 'scrape_script') as mock_scrape_script:
        all_dialog = scraper.extract_dialog('tng2')
        assert mock_scrape_script.called is False

    expected_speakers = set(['PIKARD'])

    assert len(all_dialog) > 0
    assert extract_speakers(all_dialog) == expected_speakers

    parsed_dialog = dict((s, extract_lines(all_dialog, s)) for s in expected_speakers)
    assert len(parsed_dialog['PIKARD']) == 1
    assert 'Captain\'s log. Blah blah blah.' in parsed_dialog['PIKARD']


def test_parse_script_mock_tmp():
    """Test parse_script against dummy movie TMP-formatted script."""
    scraper = stminutiae.Scraper()
    scraper.assets_path = TEST_ASSETS_PATH
    with mock.patch.object(scraper, 'scrape_script') as mock_scrape_script:
        all_dialog = scraper.extract_dialog('tmp')
        assert mock_scrape_script.called is False

    expected_speakers = set(('FLINGON CAPTAIN', 'LIEUTENANT', 'BRANCH'))

    assert len(all_dialog) > 0
    assert extract_speakers(all_dialog) == expected_speakers

    parsed_dialog = dict((s, extract_lines(all_dialog, s)) for s in expected_speakers)

    assert len(parsed_dialog['FLINGON CAPTAIN']) == 2
    assert len(parsed_dialog['LIEUTENANT']) == 2
    assert len(parsed_dialog['BRANCH']) == 1

    assert 'one two three four five six...' in parsed_dialog['FLINGON CAPTAIN']
    assert 'seven' in parsed_dialog['LIEUTENANT']
    assert '... eight nine ten eleven.. twelve.' in parsed_dialog['FLINGON CAPTAIN']
    assert 'thirteen' in parsed_dialog['BRANCH']
    assert 'fourteen' in parsed_dialog['LIEUTENANT']
