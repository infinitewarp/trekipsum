from trekipsum.scrape import sources

try:
    from unittest import mock
except ImportError:
    import mock


@mock.patch('trekipsum.scrape.sources.chakoteya.Scraper.extract_dialog')
def test_mov_tos(mock_extract_dialog):
    """Test sources.mov_tos attempts parsing expected number of movie scripts."""
    expected_count = 6
    dummy_dialog = ('SPORK', 'Fascinating.')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = sources.mov_tos(sources.chakoteya)
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count


@mock.patch('trekipsum.scrape.sources.chakoteya.Scraper.extract_dialog')
def test_tng(mock_extract_dialog):
    """Test sources.tng attempts parsing expected number of TNG scripts."""
    expected_count = 176  # TODO verify should this actually be 178?
    dummy_dialog = ('PIKARD', 'Make it so.')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = sources.tng(sources.chakoteya)
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count


@mock.patch('trekipsum.scrape.sources.chakoteya.Scraper.extract_dialog')
def test_ds9(mock_extract_dialog):
    """Test sources.ds9 attempts parsing expected number of DS9 scripts."""
    expected_count = 173  # TODO verify should this actually be 176?
    dummy_dialog = ('SISQO', 'What the hell is going on?')
    mock_extract_dialog.return_value = [dummy_dialog]

    extracted_dialog = sources.ds9(sources.chakoteya)
    assert mock_extract_dialog.call_count == expected_count
    assert len(extracted_dialog) == expected_count
    assert extracted_dialog == [dummy_dialog] * expected_count
