import shutil
import tempfile
import uuid
from os import path

import six

from trekipsum.scrape.sources import scraper

from . import TEST_ASSETS_PATH

try:
    from unittest import mock
except ImportError:
    import mock


class ConcreteTestScraper(scraper.AbstractScraper):
    """Implement abstract methods so AbstractScraper can be tested."""

    def _path_for_script_id(self, script_id):
        pass

    def _extract_from_file(self, file):
        pass


def test_extract_dialog_does_scrape_when_not_yet_on_disk():
    """Test extract_dialog scrapes script if not found on disk."""
    script_id = 1701
    scraper = ConcreteTestScraper()
    scraper.scrape_script = mock.Mock()
    scraper._extract_from_file = mock.Mock()

    def _test_in_temp_dir(tmp_dir):
        file_path = path.join(tmp_dir, str(uuid.uuid4()), str(uuid.uuid4()))
        scraper._path_for_script_id = mock.Mock(return_value=file_path)

        results = scraper.extract_dialog(script_id)

        scraper.scrape_script.assert_called_with(script_id, file_path)
        assert scraper._extract_from_file.called is False
        assert results == []

    if six.PY3:
        with tempfile.TemporaryDirectory() as tmp_dir:
            _test_in_temp_dir(tmp_dir)
    else:
        tmp_dir = tempfile.mkdtemp()
        try:
            _test_in_temp_dir(tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)


def test_extract_dialog_reads_version_from_disk():
    """Test extract_dialog uses the version already saved to disk."""
    script_id = 1701
    saved_script_path = path.join(TEST_ASSETS_PATH, 'tng.txt')
    mock_return = mock.Mock()
    scraper = ConcreteTestScraper()
    scraper._path_for_script_id = mock.Mock(return_value=saved_script_path)
    scraper._extract_from_file = mock.Mock(return_value=mock_return)

    results = scraper.extract_dialog(script_id)

    assert results == mock_return
    scraper._path_for_script_id.assert_called_with(script_id)
    assert scraper._extract_from_file.called is True


@mock.patch('trekipsum.scrape.sources.scraper.retriable_session')
def test_scrape_script(mock_retriable_session):
    """Test scrape_script successfully pulls down and writes data."""
    with open(path.join(TEST_ASSETS_PATH, 'tng.txt')) as source_file:
        dummy_script = source_file.read()

    mock_url = 'http://example.foobar/{}.txt'
    script_id = 1701
    expected_called_url = mock_url.format(script_id)
    mock_retriable_session.return_value.get.return_value.text = dummy_script

    scraper = ConcreteTestScraper()
    scraper.script_url = mock_url

    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        scraper.scrape_script(script_id, out_file.name)
        mock_retriable_session.assert_called_with()
        mock_retriable_session.return_value.get.assert_called_with(expected_called_url, timeout=1)

        out_file.seek(0)
        written_contents = out_file.read()
        assert written_contents == dummy_script


@mock.patch('trekipsum.scrape.sources.scraper.retriable_session')
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

    scraper = ConcreteTestScraper()
    scraper.script_url = mock_url

    with tempfile.NamedTemporaryFile(mode='w+') as out_file:
        scraper.scrape_script(script_id, out_file.name)
        out_file.seek(0, 2)  # seeks end of the file
        size = out_file.tell()
        assert size == 0  # file should be empty

    mock_get.assert_called_with(expected_called_url, timeout=1)
