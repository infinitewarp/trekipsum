import logging
import re
from os import path

from bs4 import BeautifulSoup

from .scraper import AbstractScraper

logger = logging.getLogger(__name__)


DEFAULT_ASSETS_PATH = path.join(
    path.dirname(path.dirname(path.dirname(path.abspath(__file__)))),
    'assets', 'chakoteya.net')
DEFAULT_SCRIPT_URL = 'http://www.chakoteya.net/StarTrek/{}.htm'


class Scraper(AbstractScraper):
    """Scrape and parse scripts from chakoteya.net."""

    def __init__(self):
        """Initialize default path to assets on disk."""
        super(Scraper, self).__init__()

        self.assets_path = DEFAULT_ASSETS_PATH
        self.script_url = DEFAULT_SCRIPT_URL

    def _extract_from_file(self, fp):
        extractor = Extractor(fp)
        return extractor.extract_lines()

    def _path_for_script_id(self, script_id):
        return path.join(self.assets_path, '{}.html'.format(script_id))


class Extractor(object):
    """Parse and extract lines of dialog from HTML script."""

    # new_speaker_matcher = re.compile(r'^([A-Z\.\-\ ]+)(\[[a-zA-Z\ ]+\])?: (.+)$')
    new_speaker_matcher = re.compile(r'^([^:]*):(.*)$')
    sub_parens = r'\(.*?\)'
    sub_braces = r'\[.*?\]'
    sub_spaces = r'\ \ +'

    speaker_corrections = {
        'MCCOY': 'BONES',
    }

    blacklisted_speakers = (
        'STARDATE',
        'ORIGINAL AIRDATE',
    )

    def __init__(self, script):
        """
        Initialize Extractor with provided script.

        Args:
            script (iterable): strings for each line of a script file
        """
        self.soup = BeautifulSoup(script, 'html.parser')

    def extract_lines(self):
        """
        Extract lines of dialog.

        Returns:
            list: list of tuples containing (speaker name, line of dialog)
        """
        self.__lines = []

        for p in self.soup.find_all('p'):
            self._reset_dialog()
            for line in p.text.split('\n'):
                line = line.strip()

                if len(line) == 0:
                    self._flush()

                new_speaker_match = self.new_speaker_matcher.match(line)
                if new_speaker_match:
                    speaker = new_speaker_match.group(1).strip()
                    text = new_speaker_match.group(2).strip()
                    self._on_new_speaker_match(speaker, text)
                else:
                    self._on_text_match(line)

            # special case to handle the very last line of dialog
            if self.__speaker is not None and len(self.__dialog) > 0:
                self._append_line()

        return self.__lines

    def _reset_dialog(self):
        self.__speaker = None
        self.__dialog = ''

    def _append_line(self):
        self.__lines.append((self.__speaker, self.__dialog))
        self._reset_dialog()

    def _flush(self):
        if len(self.__dialog) > 0 and len(self.__speaker) > 0:
            self._append_line()
        else:
            self._reset_dialog()

    def _clean_text(self, text):
        if '(' in text:
            text = re.sub(self.sub_parens, '', text)
        if '[' in text:
            text = re.sub(self.sub_braces, '', text)
        if '\t' in text:
            text = text.replace('\t', ' ')
        if '  ' in text:
            text = re.sub(self.sub_spaces, ' ', text)
        return text.strip()

    def _on_new_speaker_match(self, speaker, text):
        self._flush()

        speaker = self._clean_text(speaker).upper()
        text = self._clean_text(text)

        if ' + ' in speaker:
            speakers = map(lambda x:
                           self.speaker_corrections[x] if x in self.speaker_corrections else x,
                           text.split(' + '))
            speaker = '/'.join(sorted(speakers))
        elif speaker in self.speaker_corrections:
            speaker = self.speaker_corrections[speaker]
        elif speaker in self.blacklisted_speakers:
            return

        if len(speaker) > 0 and len(text) > 0:
            self.__speaker = speaker
            self.__dialog = text

    def _on_text_match(self, text):
        text = self._clean_text(text)
        if self.__speaker is not None:
            if len(text) > 0:
                self.__dialog = '{} {}'.format(self.__dialog, text)
        else:
            self._flush()
