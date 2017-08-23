import os
from unittest import mock

import six

from trekipsum import scrape

test_assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')


@mock.patch('trekipsum.scrape.scrape_script')
@mock.patch.object(scrape, 'assets_path', test_assets_path)
def test_parse_script_tng(mock_scrape_script):
    """Test parse_script against dummy TNG script."""
    parsed_dialog = scrape.parse_script('tng')
    assert mock_scrape_script.called is False

    assert len(parsed_dialog) > 0
    assert set(six.iterkeys(parsed_dialog)) == set(('PIKARD', 'BROI', 'DORF', 'DADA', 'Z'))

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
