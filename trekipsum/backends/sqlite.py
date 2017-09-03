import logging
import random
import sqlite3
from os import path

from ..exceptions import NoDialogFoundException, SpeakerNotFoundException

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

    def __init__(self, speaker=None):
        """Initialize with no dialog and default sqlite path."""
        self.speaker = speaker.upper() if speaker else None
        self._dialog_count = 0
        self._sqlite_path = DEFAULT_SQLITE_PATH
        self._conn = sqlite3.connect(self._sqlite_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._conn.close()

    def __del__(self, *args):
        self._conn.close()

    @property
    def dialog_count(self):
        """Lazy-load and return count of lines."""
        if self._dialog_count == 0:
            if self.speaker is None:
                self._dialog_count = self._conn.execute(self.SQL_COUNT).fetchone()[0]
            else:
                self._dialog_count = self._conn.execute(self.SQL_COUNT_BY_SPEAKER,
                                                        (self.speaker,)).fetchone()[0]
        return self._dialog_count

    def random_dialog(self):
        """
        Get random line of dialog.

        Returns:
            tuple containing (speaker name, line of dialog)
        """
        if self.dialog_count == 0:
            if self.speaker is not None:
                raise SpeakerNotFoundException(self.speaker)
            else:
                raise NoDialogFoundException()

        logger.debug('choosing random from count %s', self.dialog_count)
        offset = random.randrange(self.dialog_count)
        if self.speaker is None:
            speaker, line = self._conn.execute(self.SQL_GET_RANDOM,
                                               (offset,)).fetchone()
        else:
            speaker, line = self._conn.execute(self.SQL_GET_RANDOM_BY_SPEAKER,
                                               (self.speaker, offset)).fetchone()
        return speaker, line
