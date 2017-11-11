import logging
import random
import sqlite3
from os import path

from ..exceptions import NoDialogFoundException

logger = logging.getLogger(__name__)

DEFAULT_SQLITE_PATH = path.join(path.dirname(path.dirname(path.abspath(__file__))),
                                'assets', 'dialog.sqlite')


class DialogChooser(object):
    """Randomly choose dialog from sqlite database."""

    SQL_COUNT = 'SELECT COUNT(1) FROM dialog'
    SQL_COUNT_BY_SPEAKER = 'SELECT COUNT(1) FROM dialog WHERE speaker = ?'
    SQL_GET_RANDOM = 'SELECT speaker, line FROM dialog ORDER BY dialog_id LIMIT 1 OFFSET ?'
    SQL_GET_RANDOM_BY_SPEAKER = 'SELECT speaker, line FROM dialog WHERE speaker = ?' \
                                'ORDER BY dialog_id LIMIT 1 OFFSET ?'
    SQL_GET_RANDOM_SPEAKER = 'SELECT DISTINCT speaker FROM dialog ORDER BY RANDOM() LIMIT 1'
    SQL_GET_RANDOM_SPEAKER_EXCLUDING = 'SELECT DISTINCT speaker FROM dialog WHERE speaker <> ?' \
                                       'ORDER BY RANDOM() LIMIT 1'
    SQL_GET_ALL = 'SELECT speaker, line FROM dialog'
    SQL_GET_ALL_BY_SPEAKER = 'SELECT speaker, line FROM dialog WHERE speaker = ?'

    def __init__(self):
        """Initialize with no dialog and default sqlite path."""
        self._dialog_counts = {}
        self._sqlite_path = DEFAULT_SQLITE_PATH
        self._conn = sqlite3.connect(self._sqlite_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._conn.close()

    def __del__(self, *args):
        self._conn.close()

    def dialog_count(self, speaker=None):
        """Lazy-load and return count of lines."""
        speaker = speaker.upper() if speaker else None
        if speaker not in self._dialog_counts:
            if speaker is not None:
                count = self._conn.execute(self.SQL_COUNT_BY_SPEAKER,
                                           (speaker,)).fetchone()[0]
            else:
                count = self._conn.execute(self.SQL_COUNT).fetchone()[0]
            self._dialog_counts[speaker] = count
        return self._dialog_counts[speaker]

    def random_dialog(self, speaker=None):
        """
        Get random line of dialog, optionally limited to specific speaker.

        Returns:
            tuple containing (speaker name, line of dialog)
        """
        speaker = speaker.upper() if speaker else None
        if self.dialog_count(speaker) == 0:
            raise NoDialogFoundException(speaker)

        logger.debug('choosing random from count %s', self.dialog_count)
        offset = random.randrange(self.dialog_count(speaker))
        if speaker is None:
            speaker, line = self._conn.execute(self.SQL_GET_RANDOM,
                                               (offset,)).fetchone()
        else:
            speaker, line = self._conn.execute(self.SQL_GET_RANDOM_BY_SPEAKER,
                                               (speaker, offset)).fetchone()
        return speaker, line

    def random_speaker(self, not_speaker=None):
        """
        Get random speaker name, optionally excluding specific speaker from candidacy.
        """
        if not_speaker is None:
            return self._conn.execute(self.SQL_GET_RANDOM_SPEAKER).fetchone()[0]
        else:
            return self._conn.execute(self.SQL_GET_RANDOM_SPEAKER_EXCLUDING,
                                      (not_speaker.upper(),)).fetchone()[0]

    def all_dialog(self, speaker=None):
        """
        Yield all available dialog, optionally limited to specific speaker.

        Returns:
            generator of tuples containing (speaker name, line of dialog)
        """
        if speaker is not None:
            speaker = speaker.upper()
            result = self._conn.execute(self.SQL_GET_ALL_BY_SPEAKER, (speaker,))
        else:
            result = self._conn.execute(self.SQL_GET_ALL)
        row = result.fetchone()
        while row is not None:
            yield row
            row = result.fetchone()
