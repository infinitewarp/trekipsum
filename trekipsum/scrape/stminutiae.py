import logging
import os
import re

import requests

from .utils import magicdictset

logger = logging.getLogger(__name__)


DEFAULT_ASSETS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets')


class Scraper(object):
    """Scrape and parse scripts from st-minutiae.com."""

    def __init__(self):
        """Initialize regexes and default path to assets on disk."""
        self.assets_path = DEFAULT_ASSETS_PATH
        # https://regex101.com/r/WBYM0F/1
        self.speaker_matcher = re.compile(r'^(?:\t{5}|\ {43})\"?(?!ACT)((?:[a-zA-Z0-9#\-/&]|\.[\ \w]|\.(?=\')|\ (?!V\.O\.|\(|COM\ )|\'(?!S(?![\w])))+)\.?.*$')  # noqa
        self.dialog_matcher = re.compile(r'^(?:\t{3}|\ {29}|\ {30})([^\t\ ].+)$')
        self.break_matcher = re.compile(r'^\s*END OF ACT')

    def extract_lines(self, script):
        """
        Extract lines of dialog from a script.

        Args:
            script (list): list of strings that make up a script

        Returns:
            dict: speaker names as keys with lists of strings for their dialog
        """
        lines = magicdictset()
        current_speaker = None
        current_dialog = ''
        dialog_counter = 0
        for line in script:
            # if we find what appears to be a break in dialog, save the current thread and reset
            # thread.
            break_match = self.break_matcher.match(line)
            if break_match and current_speaker is not None and len(current_dialog) > 0:
                lines[current_speaker].add(current_dialog)
                dialog_counter += 1
                current_dialog = ''
                continue

            # if we find a line of dialog, append it to a running thread of dialog
            dialog_match = self.dialog_matcher.match(line)
            if dialog_match:
                new_dialog = dialog_match.group(1).strip()
                if len(current_dialog) > 0:
                    if current_dialog.endswith('...'):
                        current_dialog = current_dialog.rstrip('. ')
                    if new_dialog.startswith('...'):
                        new_dialog = new_dialog.lstrip('. ')
                current_dialog = '{} {}'.format(current_dialog, new_dialog).strip()
                continue

            # if we find a new speaker, save the current thread for the last speaker, reset speaker,
            # and reset thread.
            speaker_match = self.speaker_matcher.match(line)
            if speaker_match:
                new_speaker = speaker_match.group(1).upper().strip()
                if current_speaker != new_speaker:
                    if len(current_dialog) > 0:
                        if current_speaker is None:
                            logger.error('discarding dialog with no speaker: %s', current_dialog)
                        else:
                            current_dialog = current_dialog.replace('... ...', '')
                            lines[current_speaker].add(current_dialog)
                            dialog_counter += 1
                    current_speaker = new_speaker
                    current_dialog = ''

        if current_speaker is not None and len(current_dialog) > 0:
            current_dialog = current_dialog.replace('... ...', '')
            lines[current_speaker].add(current_dialog)
            dialog_counter += 1

        logger.debug('found %s spoken lines for %s speakers', dialog_counter, len(lines.keys()))
        return lines

    def parse_script(self, script_id):
        """Parse plaintext script, downloading file if needed."""
        file_path = os.path.join(self.assets_path, '{}.txt'.format(script_id))
        if not os.path.isfile(file_path):
            self.scrape_script(script_id, file_path)
        lines = magicdictset()
        if os.path.isfile(file_path):
            with open(file_path) as f:
                logger.debug('extracting dialog from %s', file_path)
                lines = self.extract_lines(f)
        return lines

    def scrape_script(self, script_id, to_file_path):
        """Scrape script from st-minutiae.com."""
        url = 'http://www.st-minutiae.com/resources/scripts/{}.txt'.format(script_id)
        logger.debug('attempting to download script from %s', url)
        response = requests.get(url)
        if response:
            with open(to_file_path, mode='w') as f:
                f.write(response.text)
        else:
            logger.error('could not fetch %s: %s %s',
                         response.url, response.status_code, response.reason)
