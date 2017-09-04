import abc
import logging
import os
from os import path

from ..utils import retriable_session

logger = logging.getLogger(__name__)


class AbstractScraper(object):
    """Scrape and parse scripts."""

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """Initialize with requests session."""
        self.session = retriable_session()
        self.script_url = None

    def extract_dialog(self, script_id):
        """Parse and extract dialog from script, downloading if needed."""
        file_path = self._path_for_script_id(script_id)
        if not path.isdir(path.dirname(file_path)):
            os.makedirs(path.dirname(file_path))
        if not path.isfile(file_path):
            self.scrape_script(script_id, file_path)
        if path.isfile(file_path):
            with open(file_path, 'r') as f:
                logger.debug('extracting dialog from %s', file_path)
                return self._extract_from_file(f)
        else:
            return []

    @abc.abstractmethod
    def _path_for_script_id(self, script_id):
        """Generate file path for the given script_id."""

    @abc.abstractmethod
    def _extract_from_file(self, file):
        """Extract lines from the open file."""

    def _clean_response_text(self, response_text):
        """Clean the response text before writing to disk."""
        return response_text

    def scrape_script(self, script_id, to_file_path):
        """Scrape script from st-minutiae.com."""
        url = self.script_url.format(script_id)
        logger.debug('attempting to download script from %s', url)
        response = self.session.get(url, timeout=1.0)
        if response:
            with open(to_file_path, mode='w') as f:
                clean_text = self._clean_response_text(response.text)
                f.write(clean_text)
        else:
            logger.warning('could not fetch %s: %s %s',
                           response.url, response.status_code, response.reason)
