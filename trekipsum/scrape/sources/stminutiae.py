import logging
import re
from os import path

import six

from .scraper import AbstractScraper

logger = logging.getLogger(__name__)


DEFAULT_ASSETS_PATH = path.join(
    path.dirname(path.dirname(path.abspath(__file__))),
    'assets', 'st-minutiae.com')
DEFAULT_SCRIPT_URL = 'http://www.st-minutiae.com/resources/scripts/{}.txt'


class Scraper(AbstractScraper):
    """Scrape and parse scripts from st-minutiae.com."""

    def __init__(self):
        """Initialize default path to assets on disk."""
        super(Scraper, self).__init__()

        self.assets_path = DEFAULT_ASSETS_PATH
        self.script_url = DEFAULT_SCRIPT_URL

        # control_chars to be stripped from text.
        # 103, 131, 227 are known to be problematic.
        self._control_chars = list(range(32))
        self._control_chars.remove(9)
        self._control_chars.remove(10)
        if six.PY2:
            # because PY2's `translate` behaves differently
            self._control_chars = [chr(c) for c in self._control_chars]

    def _clean_response_text(self, text):
        if six.PY2:
            return str.translate(text, None, ''.join(self._control_chars))
        return text.translate(dict.fromkeys(self._control_chars))

    def _extract_from_file(self, f):
        extractor = Extractor(f)
        return extractor.extract_lines()

    def _path_for_script_id(self, script_id):
        return path.join(self.assets_path, '{}.txt'.format(script_id))


class Extractor(object):
    """Parse and extract lines of dialog from a script."""

    # https://regex101.com/r/WBYM0F/1
    speaker_matcher = re.compile(r'^(?:\t{5}|\ {43})\"?(?!ACT)((?:[a-zA-Z0-9#\-/&]|\.[\ \w]|\.(?=\')|\ (?!V\.O\.|\(|COM\ )|\'(?!S(?![\w])))+)\.?.*$')  # noqa
    dialog_matcher = re.compile(r'^(?:\t{3}|\t{6}|\ {29}|\ {30})([^\t\ ].+)$')
    break_matcher = re.compile(r'^\s*END OF ')

    speaker_corrections = {
        '0\'BRIEN': 'O\'BRIEN',
        'CRUSHER': 'BEVERLY',
        'EE I CHAR': 'EE\'CHAR',
        'ENSIGN RO': 'RO',
        'LA FORGE': 'GEORDI',
        'SCOTT': 'SCOTTY',
        'WES': 'WESLEY',
    }

    blacklisted_speakers = (
        'STORY BY',
        'SHOOTING SCRIPT',
        'JULY 19',
    )

    def __init__(self, script):
        """
        Initialize Extractor with provided script.

        Args:
            script (iterable): strings for each line of a script file
        """
        self.script = script

    def extract_lines(self):
        """
        Extract lines of dialog.

        Returns:
            list: list of tuples containing (speaker name, line of dialog)
        """
        self.__lines = []
        self._reset_dialog()

        for line in self.script:
            # if we find what appears to be a hard break in dialog,
            # save the current thread and reset the running dialog.
            break_match = self.break_matcher.match(line)
            if break_match and self.__speaker is not None and len(self.__dialog) > 0:
                self._append_line()
                continue

            dialog_match = self.dialog_matcher.match(line)
            if dialog_match:
                text = dialog_match.group(1).strip()
                self._on_dialog_match(text)
                continue

            speaker_match = self.speaker_matcher.match(line)
            if speaker_match:
                text = speaker_match.group(1).upper().strip()
                if text:
                    self._on_speaker_match(text)

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

    def _on_dialog_match(self, text):
        """Clean up and append the text to the running dialog."""
        if text.endswith('..'):
            # clean up lines ending with ellipses
            text = '{}...'.format(text.rstrip('. '))

        if text.startswith('..'):
            # clean up lines starting with ellipses
            text = text.lstrip('. ')
            if len(self.__dialog) == 0:
                # only include opening ellipsis if this is the start of dialog
                text = '...{}'.format(text)

        # Join with existing dialog.
        self.__dialog = '{} {}'.format(self.__dialog, text).strip()

        if '- ' in self.__dialog:
            # fix some weird hyphenation spacing issues
            self.__dialog, _ = re.subn(
                r'(.*[a-zA-Z]-)( )(.*)',
                r'\1\3',
                self.__dialog
            )

    def _on_speaker_match(self, text):
        """
        Handle text line when it appears to be a speaker.

        Upon finding a speaker, if it's different from the last known speaker, save the dialog
        for that last speaker and start tracking for the new speaker.
        """
        if text[-1] == '.' and '.' not in text[:-1]:
            text = text[:-1]  # strip trailing dot

        if ' AND ' in text:
            text = text.replace(' AND ', '/')
        if ' & ' in text:
            text = text.replace(' & ', '/')
        if '/' in text:
            speakers = map(lambda x:
                           self.speaker_corrections[x] if x in self.speaker_corrections else x,
                           text.split('/'))
            text = '/'.join(sorted(speakers))
        elif text in self.speaker_corrections:
            text = self.speaker_corrections[text]

        if self.__speaker != text:
            if len(self.__dialog) > 0:
                if self.__speaker is None:
                    logger.debug('discarding dialog with no speaker: %s', self.__dialog)
                    self._reset_dialog()
                else:
                    self._append_line()
            if text not in self.blacklisted_speakers:
                self.__speaker = text
