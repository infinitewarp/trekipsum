# -*- coding: utf-8 -*-
import logging
import re
import string
import uuid
from os import path

from bs4 import BeautifulSoup

from .scraper import AbstractScraper

logger = logging.getLogger(__name__)


DEFAULT_ASSETS_PATH = path.join(
    path.dirname(path.dirname(path.dirname(path.abspath(__file__)))),
    'assets', 'chakoteya.net')
# DEFAULT_SCRIPT_URL = 'http://www.chakoteya.net/{}'
# It seems chakoteya.net aggressively blocks you if you scrape content. So...
# DEFAULT_SCRIPT_URL = 'https://webcache.googleusercontent.com/search?q=cache:' \
#                      'http://www.chakoteya.net/{}'
# NOTE: Google might also gets upset with a frequent smashing of requests.
DEFAULT_SCRIPT_URL = 'https://web.archive.org/web/20170627150655/www.chakoteya.net/{}'

ids = {
    'tos': tuple('StarTrek/{}.htm'.format(i) for i in range(1, 80)),
    'tas': tuple('StarTrek/TAS{:03d}.htm'.format(i) for i in range(1, 24) if i not in (9, 12)),
    'tng': tuple('NextGen/{}.htm'.format(i) for i in range(101, 278) if i not in (102,)),
    'ds9': tuple('DS9/{}.htm'.format(i) for i in range(401, 576) if i not in (402, 474)),
    'voy': tuple('Voyager/{}.htm'.format(i) for i in
                 # 101-119, 201-225, 301-321, 401-423, 501-525, 601-625, 701-722
                 tuple(range(101, 120)) +
                 tuple(range(201, 226)) +
                 tuple(range(301, 322)) +
                 tuple(range(401, 424)) +
                 tuple(range(501, 526)) +
                 tuple(range(601, 626)) +
                 tuple(range(701, 723))),
    'ent': tuple('Enterprise/{:02d}.htm'.format(i) for i in range(1, 99) if i != 2),
    'mov_tos': tuple('movies/movie{}.html'.format(i) for i in range(1, 7)),
    'mov_tng': tuple('movies/movie{}.html'.format(i) for i in range(7, 11)),
}


class Scraper(AbstractScraper):
    """Scrape and parse scripts from chakoteya.net."""

    def __init__(self):
        """Initialize default path to assets on disk."""
        super(Scraper, self).__init__()

        self.assets_path = DEFAULT_ASSETS_PATH
        self.script_url = DEFAULT_SCRIPT_URL
        self.timeout = 5.0  # increase because web.archive.org can be slow

    def _extract_from_file(self, fp):
        extractor = Extractor(fp)
        return extractor.extract_lines()

    def _path_for_script_id(self, script_id):
        return path.join(self.assets_path, '{}'.format(script_id))


class Extractor(object):
    """Parse and extract lines of dialog from HTML script."""

    line_with_speaker_matcher = re.compile(r'^([^:]*):(.*)$')
    captains_log_matcher = re.compile(r'.*\w\'S\ (?:PERSONAL\ )?(?:STAR)?LOG.*')
    speaker_semicolon_matcher = re.compile(r'^([A-Z\ \[\]\.]+);(.*)')

    sub_parens = r'\(.*?\)'
    sub_parens_without_open = r'^[^\(]*?\)'
    sub_parens_without_close = r'\([^\)]*$'
    sub_braces = r'\[.*?\]'
    sub_braces_without_open = r'^[^\[]*?\]'
    sub_braces_without_close = r'\[[^\]]*$'
    sub_curly = r'{.*?}'
    sub_curly_without_open = r'^[^{]*?}'
    sub_curly_without_close = r'{[^}]*$'
    sub_spaces = r'\ \ +'
    sub_ellipsis = r'([^\s])\s+\.{3}([A-Za-z])'
    sub_ellipsis_replace = r'\1 \2'

    speaker_corrections = {
        '#2': 'CREWMAN #2',
        '.JANEWAY': 'JANEWAY',
        '0\'BRIEN': 'O\'BRIEN',
        '\' GILMORE': 'GILMORE',
        'ALICE 118+2': 'ALICE 118/ALICE 2',
        'ALIEN 1+4': 'ALIEN 1/ALIEN 4',
        'ALL EXCEPT MARTOK': 'ALL',
        'AQUATIC2': 'AQUATIC 2',
        'B-4 HEAD': 'B-4',
        'BEVERLY': 'CRUSHER',
        'COMM. OFFICER': 'COMM OFFICER',
        'DAX.': 'DAX',
        'DILLARD?': 'DILLARD',
        'G SPOCK': 'SPOCK',
        'JEAN LUC': 'PICARD',
        'JEAN-LUC': 'PICARD',
        'KIM|': 'KIM',
        'LAFORGE': 'GEORDI',
        'MARIE': 'MARIE PICARD',
        'MAURICE': 'MAURICE PICARD',
        'MCCOY': 'BONES',
        'MCCOY2': 'BONES',
        'O\'BRIEN ET AL': 'O\'BRIEN',
        'PARIS?STETH': 'PARIS/STETH',
        'PASSER-BY': 'PASSERBY',
        'PICARD\'S CHILDREN':
            'MATTHEW PICARD/MIMI PICARD/THOMAS PICARD/MADISON PICARD/OLIVIA PICARD',
        'REN\' PICARD': 'RENÉ PICARD',
        'RENE': 'RENÉ PICARD',
        'RODRIQUEZ': 'RODRIGUEZ',
        'T\'GRETH?': 'T\'GRETH',
    }

    blacklisted_speakers = (
        'STARDATE',
        'ORIGINAL AIRDATE',
        'LAST TIME ON STAR TREK',
    )

    script_ends = (
        'END CREDITS',
        'CREDITS',
        'THE HUMAN ADVENTURE IS JUST BEGINNING.',
        '...AND THE ADVENTURE CONTINUES...',
    )

    br_separator_token = str(uuid.uuid4())

    def __init__(self, script):
        """
        Initialize Extractor with provided script.

        Args:
            script (iterable): strings for each line of a script file
        """
        self.script = '\n'.join(script)

    def extract_lines(self):
        """
        Extract lines of dialog.

        Returns:
            list: list of tuples containing (speaker name, line of dialog)
        """
        self.__lines = []
        script = self.script.replace('</p>', '').replace('<p>', '<br>')
        script = script.replace('<b>', '').replace('</b>', '')
        script = script.replace('\n.\n', '\n\n')
        soup = BeautifulSoup(script, 'html.parser')

        self._reset_dialog()
        for br in soup.find_all('br'):
            br.replace_with(self.br_separator_token)

        body_text = soup.find('table').text
        body_text = body_text.replace('\n', ' ')
        body_text = body_text.replace(self.br_separator_token, '\n\n')
        in_break = False
        for line in body_text.split('\n'):
            line = line.strip()

            if len(line) == 0:
                if in_break:
                    self._flush()
                else:
                    in_break = True
                continue

            in_break = False
            if self._is_end_of_script(line):
                self._flush()
                break

            speaker_semicolon_match = self.speaker_semicolon_matcher.match(line)
            if speaker_semicolon_match:
                line = '{}:{}'.format(speaker_semicolon_match.group(1),
                                      speaker_semicolon_match.group(2))

            line_with_speaker_match = self.line_with_speaker_matcher.match(line)
            if line_with_speaker_match:
                speaker = line_with_speaker_match.group(1).strip()
                text = line_with_speaker_match.group(2).strip()
                self._on_speaker_and_text_match(speaker, text)
                continue
            else:
                self._on_text_only_match(line)
                continue

        # special case to handle the very last line of dialog
        if len(self.__speaker) > 0 and len(self.__dialog) > 0:
            self._append_line()

        return self.__lines

    def _reset_dialog(self):
        self.__speaker = ''
        self.__dialog = ''

    def _append_line(self):
        self.__dialog = self._clean_text(self.__dialog)
        self.__speaker = self._clean_text(self.__speaker)

        if len(self.__speaker) > 0 and len(self.__dialog) > 0:
            if self.__dialog[-1] not in string.punctuation:
                # dialog ending mid-stride is bad
                self.__dialog += '...'
            self.__lines.append((self.__speaker, self.__dialog))
        self._reset_dialog()

    def _flush(self):
        if len(self.__dialog) > 0 and len(self.__speaker) > 0:
            self._append_line()
        else:
            self._reset_dialog()

    def _clean_text(self, text):
        if '(' in text:  # strip parentheticals
            text = re.sub(self.sub_parens, '', text)
        if ')' in text:  # strip partial parens with no opening
            text = re.sub(self.sub_parens_without_open, '', text, count=1)
        if '(' in text:  # strip partial parens with no closing
            text = re.sub(self.sub_parens_without_close, '', text, count=1)
        if '[' in text:  # strip braced blocks
            text = re.sub(self.sub_braces, '', text)
        if ']' in text:  # strip partial braced blocks with no opening
            text = re.sub(self.sub_braces_without_open, '', text, count=1)
        if '[' in text:  # strip partial braced blocks with no closing
            text = re.sub(self.sub_braces_without_close, '', text, count=1)
        if '{' in text:  # strip curly brace blocks
            text = re.sub(self.sub_curly, '', text)
        if '}' in text:  # strip partial curly brace blocks with no opening
            text = re.sub(self.sub_curly_without_open, '', text, count=1)
        if '{' in text:  # strip partial curly braced block with no closing
            text = re.sub(self.sub_curly_without_close, '', text, count=1)
        if '\t' in text:
            text = text.replace('\t', ' ')
        if '  ' in text:  # collapse multiple spaces to one
            text = re.sub(self.sub_spaces, ' ', text)
        if '...' in text:
            text = re.sub(self.sub_ellipsis, self.sub_ellipsis_replace, text)
        if u'�' in text:
            text = text.replace('�', '\'')
        if u'�' in text:
            text = text.replace('�', 'é')
        if u'�' in text:
            text = text.replace('�', 'É')
        return text.strip()

    def _is_end_of_script(self, text):
        if text.startswith('&lt;Back'):
            return True
        if text in self.script_ends:
            return True
        return False

    def _on_speaker_and_text_match(self, speaker, text):
        speaker = self._clean_text(speaker).upper()

        if self.captains_log_matcher.match(speaker):
            # TODO better handling of captain's logs
            # NOTE ranks other than captain make these logs too
            self._flush()
            return

        if speaker.endswith('\'S VOICE'):
            speaker = speaker[:-len('\'S VOICE')]

        if speaker in self.speaker_corrections:
            speaker = self.speaker_corrections[speaker]
        elif speaker in self.blacklisted_speakers:
            return

        for conjunction in {'+', ' AND ', '/', ','}:
            if conjunction in speaker:
                speakers = map(lambda x:
                               self.speaker_corrections[x.strip()]
                               if x.strip() in self.speaker_corrections
                               else x.strip(),
                               speaker.split(conjunction))
                speaker = '/'.join(sorted(speakers))

        if len(speaker) == 0 or len(text) == 0:
            return

        if speaker != self.__speaker:
            self._flush()
            self.__speaker = speaker
            self.__dialog = text
        else:
            self.__dialog = '{} {}'.format(self.__dialog, text)

    def _on_text_only_match(self, text):
        if self.captains_log_matcher.match(text.upper()):
            # TODO better handling of captain's logs
            # NOTE ranks other than captain make these logs too
            self._flush()

        if len(self.__speaker) > 0:
            if len(text) > 0:
                self.__dialog = '{} {}'.format(self.__dialog, text)
        else:
            self._reset_dialog()
