import os

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


def test_parse_script_mock_tng():
    """Test parse_script against dummy TNG-formatted script."""
    scraper = stminutiae.Scraper()
    scraper.assets_path = TEST_ASSETS_PATH
    with mock.patch.object(scraper, 'scrape_script') as mock_scrape_script:
        all_dialog = scraper.extract_dialog('tng')
        assert mock_scrape_script.called is False

    expected_speakers = set(('PIKARD', 'BROI', 'DORF', 'DADA', 'Z'))

    assert len(all_dialog) > 0
    assert extract_speakers(all_dialog) == expected_speakers

    parsed_dialog = dict((s, extract_lines(all_dialog, s)) for s in expected_speakers)
    assert len(parsed_dialog['PIKARD']) == 9
    assert len(parsed_dialog['BROI']) == 2
    assert len(parsed_dialog['DORF']) == 3
    assert len(parsed_dialog['DADA']) == 5
    assert len(parsed_dialog['Z']) == 5

    assert 'one two three four five six seven eight nine ten eleven twelve thirteen. fourteen ' \
           'fifteen?' in parsed_dialog['PIKARD']
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
    assert 'forty-eight' in parsed_dialog['DORF']
    assert 'forty-nine' in parsed_dialog['Z']
    assert 'fifty' in parsed_dialog['DORF']


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
