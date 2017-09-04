from trekipsum.scrape.sources import chakoteya

from . import TEST_ASSETS_PATH, extract_lines, extract_speakers

try:
    from unittest import mock
except ImportError:
    import mock


def test_parse_script_mock_tos():
    """Test parse_script against dummy TOS HTML-formatted script."""
    scraper = chakoteya.Scraper()
    scraper.assets_path = TEST_ASSETS_PATH
    with mock.patch.object(scraper, 'scrape_script') as mock_scrape_script:
        all_dialog = scraper.extract_dialog('tos')
        assert mock_scrape_script.called is False

    expected_speakers = {'SPORK', 'SOLO', 'DIRK', 'CHURCH', 'BONES'}

    assert len(all_dialog) > 0
    assert extract_speakers(all_dialog) == expected_speakers

    parsed_dialog = dict((s, extract_lines(all_dialog, s)) for s in expected_speakers)
    assert len(parsed_dialog['SPORK']) == 4
    assert len(parsed_dialog['SOLO']) == 2
    assert len(parsed_dialog['DIRK']) == 4
    assert len(parsed_dialog['CHURCH']) == 3
    assert len(parsed_dialog['BONES']) == 3

    assert 'one, two?' in parsed_dialog['SPORK']
    assert 'three' in parsed_dialog['SOLO']
    assert 'four, Mister Spork.' in parsed_dialog['DIRK']
    assert 'five' in parsed_dialog['SPORK']
    assert 'six' in parsed_dialog['SOLO']
    assert 'seven' in parsed_dialog['CHURCH']
    assert 'eight' in parsed_dialog['BONES']
    assert 'nine ten.' in parsed_dialog['CHURCH']
    assert 'eleven?' in parsed_dialog['DIRK']
    assert 'twelve thirteen.' in parsed_dialog['BONES']
    # TODO how to handle "captain's log" lines?
    # Captain's log, stardate 5432.2. fourteen fifteen sixteen.
    assert 'seventeen' in parsed_dialog['DIRK']
    assert 'eighteen' in parsed_dialog['SPORK']
    assert 'nineteen' in parsed_dialog['CHURCH']
    assert 'twenty twenty-one twenty-two.' in parsed_dialog['SPORK']
    assert 'twenty-three twenty-four.' in parsed_dialog['BONES']
    assert 'twenty-five twenty-six twenty-seven.' in parsed_dialog['DIRK']
