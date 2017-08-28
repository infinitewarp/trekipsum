from __future__ import print_function

import argparse
import logging
import os
import pickle
import random

import six

logger = logging.getLogger(__name__)


class SpeakerNotFoundException(Exception):
    """Exception for when trying to access dialog for a speaker who has none."""

    def __init__(self, speaker):
        """Initialize with appropriate message."""
        message = 'Speaker "{}" has no known dialog.'.format(speaker)
        super(SpeakerNotFoundException, self).__init__(message)
        self.speaker = speaker


class RandomDialogChooser(object):
    """Randomly choose dialog from pickled data."""

    def __init__(self, speaker=None):
        """Initialize with no dialog and default pickle path."""
        self.speaker = speaker.upper() if speaker else None
        self._all_dialog = None
        self._dialog_count = 0
        self._pickle_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                         'assets', 'all_dialog.pickle')

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
        logger.debug('shoosing random from count %s', self.dialog_count)
        offset = random.randrange(self.dialog_count)
        for speaker, lines in six.iteritems(self.all_dialog):
            count = len(lines)
            if offset >= count:
                offset -= count
                continue
            return speaker, lines[offset]


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='TrekIpsum generator')
    parser.add_argument('--speaker', type=str, help='limit output to this speakers')
    parser.add_argument('--no-attribute', help='hide speaker attribution', action='store_true')
    parser.add_argument('--count', type=int, default=1, help='lines of dialog to output')
    parser.add_argument('--debug', help='enable debug logging', action='store_true')
    return parser.parse_args()


def print_dialog(line, speaker, show_speaker=False):
    """Print the line and speaker, formatted appropriately."""
    line = line.__repr__()
    if show_speaker:
        speaker = speaker.title()
        print('{} -- {}'.format(line, speaker))
    else:
        print(line)


def main_cli():
    """Execute module as CLI program."""
    args = parse_cli_args()
    loglevel = logging.DEBUG if args.debug else logging.CRITICAL
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s')
    logger.setLevel(loglevel)
    chooser = RandomDialogChooser(speaker=args.speaker)
    for _ in range(args.count):
        speaker, line = chooser.random_dialog()
        print_dialog(line, speaker, not args.no_attribute)
