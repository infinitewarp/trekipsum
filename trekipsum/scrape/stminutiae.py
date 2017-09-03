import logging
import os
import re

import six

from trekipsum.scrape.utils import retriable_session

logger = logging.getLogger(__name__)


DEFAULT_ASSETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
DEFAULT_SCRIPT_URL = 'http://www.st-minutiae.com/resources/scripts/{}.txt'


class Scraper(object):
    """Scrape and parse scripts from st-minutiae.com."""

    def __init__(self):
        """Initialize default path to assets on disk."""
        self.assets_path = DEFAULT_ASSETS_PATH
        self.script_url = DEFAULT_SCRIPT_URL
        self.session = retriable_session()

    def extract_dialog(self, script_id):
        """Parse plaintext script, downloading file if needed."""
        file_path = os.path.join(self.assets_path, '{}.txt'.format(script_id))
        if not os.path.isfile(file_path):
            self.scrape_script(script_id, file_path)
        if os.path.isfile(file_path):
            with open(file_path) as f:
                logger.debug('extracting dialog from %s', file_path)
                extractor = Extractor(f)
                return extractor.extract_lines()

    def scrape_script(self, script_id, to_file_path):
        """Scrape script from st-minutiae.com."""
        url = self.script_url.format(script_id)
        logger.debug('attempting to download script from %s', url)
        response = self.session.get(url, timeout=1.0)
        if response:
            with open(to_file_path, mode='w') as f:
                # 103, 131, 227? are known problematic
                control_chars = list(range(32))
                control_chars.remove(9)
                control_chars.remove(10)
                if six.PY3:
                    clean_text = response.text.translate(dict.fromkeys(control_chars))
                else:
                    control_chars = [chr(c) for c in control_chars]
                    clean_text = str.translate(response.text, None, ''.join(control_chars))
                f.write(clean_text)
        else:
            logger.warning('could not fetch %s: %s %s',
                           response.url, response.status_code, response.reason)


class Extractor(object):
    """Parse and extract lines of dialog from a script."""

    def __init__(self, script):
        """
        Initialize regexes for parsing scripts.

        Args:
            script (iterable): strings for each line of a script file
        """
        self.script = script

        # https://regex101.com/r/WBYM0F/1
        self.speaker_matcher = re.compile(r'^(?:\t{5}|\ {43})\"?(?!ACT)((?:[a-zA-Z0-9#\-/&]|\.[\ \w]|\.(?=\')|\ (?!V\.O\.|\(|COM\ )|\'(?!S(?![\w])))+)\.?.*$')  # noqa
        self.dialog_matcher = re.compile(r'^(?:\t{3}|\t{6}|\ {29}|\ {30})([^\t\ ].+)$')
        self.break_matcher = re.compile(r'^\s*END OF ')

        self.blacklisted_speakers = (
            'STORY BY',
            'SHOOTING SCRIPT',
            'JULY 19',
        )

        self.speaker_corrections = {
            'WES': 'WESLEY',
            'EE I CHAR': 'EE\'CHAR',
            'CRUSHER': 'BEVERLY',
        }

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
            speakers = text.split('/')
            text = '/'.join(sorted(text.split('/')))

        if text in self.speaker_corrections:
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
