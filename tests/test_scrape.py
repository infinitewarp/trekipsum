import os

import mock

from trekipsum import scrape

test_assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')


@mock.patch('trekipsum.scrape.scrape_script')
@mock.patch.object(scrape, 'assets_path', test_assets_path)
def test_parse_script_mock_tng(mock_scrape_script):
    """Test parse_script against dummy TNG-formatted script."""
    parsed_dialog = scrape.parse_script('tng')
    assert mock_scrape_script.called is False

    assert len(parsed_dialog) > 0
    assert set(parsed_dialog.keys()) == set(('PIKARD', 'BROI', 'DORF', 'DADA', 'Z'))

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


@mock.patch('trekipsum.scrape.scrape_script')
@mock.patch.object(scrape, 'assets_path', test_assets_path)
def test_parse_script_mock_tmp(mock_scrape_script):
    """Test parse_script against dummy movie TMP-formatted script."""
    parsed_dialog = scrape.parse_script('tmp')
    assert mock_scrape_script.called is False

    assert len(parsed_dialog) > 0
    assert set(parsed_dialog.keys()) == set(('FLINGON CAPTAIN', 'LIEUTENANT', 'BRANCH'))

    assert len(parsed_dialog['FLINGON CAPTAIN']) == 2
    assert len(parsed_dialog['LIEUTENANT']) == 2
    assert len(parsed_dialog['BRANCH']) == 1

    assert 'one two three four five six...' in parsed_dialog['FLINGON CAPTAIN']
    assert 'seven' in parsed_dialog['LIEUTENANT']
    assert '... eight nine ten eleven.. twelve.' in parsed_dialog['FLINGON CAPTAIN']
    assert 'thirteen' in parsed_dialog['BRANCH']
    assert 'fourteen' in parsed_dialog['LIEUTENANT']


@mock.patch('trekipsum.scrape.parse_script')
def test_parse_movies(mock_parse_script):
    """Test parse_movies attempts parsing expected number of movie scripts."""
    expected_count = 9  # TODO fix 'fc' script and add abrams movies; this should be 10 or 13
    parsed_scripts = scrape.parse_movies()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count


@mock.patch('trekipsum.scrape.parse_script')
def test_parse_tng(mock_parse_script):
    """Test parse_tng attempts parsing expected number of TNG scripts."""
    expected_count = 176  # TODO verify should this actually be 178?
    parsed_scripts = scrape.parse_tng()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count


@mock.patch('trekipsum.scrape.parse_script')
def test_parse_ds9(mock_parse_script):
    """Test parse_ds9 attempts parsing expected number of DS9 scripts."""
    expected_count = 174  # TODO verify should this actually be 176?
    parsed_scripts = scrape.parse_ds9()
    assert mock_parse_script.call_count == expected_count
    assert len(parsed_scripts) == expected_count
