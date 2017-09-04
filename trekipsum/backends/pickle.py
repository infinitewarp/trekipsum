"""
Pickle-based dialog chooser is deprecated.
"""
from __future__ import absolute_import

import logging
import pickle
import random
from os import path

import six

from ..exceptions import SpeakerNotFoundException

logger = logging.getLogger(__name__)

DEFAULT_PICKLE_PATH = path.join(path.dirname(path.dirname(path.abspath(__file__))),
                                'assets', 'dialog.pickle')


class DialogChooser(object):
    """Randomly choose dialog from pickled data."""

    def __init__(self, speaker=None):
        """Initialize with no dialog and default pickle path."""
        self.speaker = speaker.upper() if speaker else None
        self._all_dialog = None
        self._dialog_count = 0
        self._pickle_path = DEFAULT_PICKLE_PATH

    @property
    def dialog_count(self):
        """Lazy-load and return count of all speakers' lines."""
        if self._dialog_count == 0:
            self._dialog_count = sum(len(lines) for _, lines in six.iteritems(self.all_dialog))
        return self._dialog_count

    @property
    def all_dialog(self):
        """Lazy-load and return all dialog."""
        if self._all_dialog is None:
            logger.debug('no dialog found; loading from pickle')
            with open(self._pickle_path, mode='rb') as pickle_file:
                self._all_dialog = pickle.load(pickle_file)
            if self.speaker is not None:
                if self.speaker not in self.all_dialog:
                    raise SpeakerNotFoundException(self.speaker)
                self._all_dialog = {
                    self.speaker: self._all_dialog[self.speaker]
                }
            for speaker in self._all_dialog.keys():
                count = len(self._all_dialog[speaker])
                logger.debug('%s has %s dialog lines', speaker, count)
                self._dialog_count += count
            logger.debug('%s lines of dialog loaded for %s speakers',
                         self._dialog_count, len(self._all_dialog.keys()))
        return self._all_dialog

    def random_dialog(self):
        """
        Get random line of dialog.

        Returns:
            tuple containing (speaker name, line of dialog)
        """
        logger.debug('choosing random from count %s', self.dialog_count)
        offset = random.randrange(self.dialog_count)
        for speaker, lines in six.iteritems(self.all_dialog):
            count = len(lines)
            if offset >= count:
                offset -= count
                continue
            return speaker, lines[offset]
