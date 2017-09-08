from __future__ import print_function

import argparse
import logging

from trekipsum import backends

logger = logging.getLogger(__name__)


def positive(value):
    """Type check value is a natural number (positive nonzero integer)."""
    value = int(value)
    if value < 1:
        raise ValueError()
    return value


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='TrekIpsum generator')
    parser.add_argument('--speaker', type=str,
                        help='limit output to this speakers')
    parser.add_argument('-a', '--attribute', action='store_true',
                        help='include speaker attribution')
    parser.add_argument('-n', '--paragraphs', type=positive, default=3,
                        help='number of paragraphs to output (default: %(default)s)')
    parser.add_argument('-s', '--sentences', type=positive, default=4,
                        help='number of sentences per paragraph (default: %(default)s)')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug logging')
    return parser.parse_args()


def print_dialog(line, speaker, show_speaker=False):
    """Print the line and speaker, formatted appropriately."""
    if show_speaker:
        speaker = speaker.title()
        print('{} -- {}'.format(line.__repr__(), speaker))
    else:
        print(line)


def main_cli():
    """Execute module as CLI program."""
    args = parse_cli_args()
    loglevel = logging.DEBUG if args.debug else logging.CRITICAL
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(message)s')
    logger.setLevel(loglevel)
    chooser = backends.SqliteRandomChooser()
    for paragraph in range(args.paragraphs):
        speaker = args.speaker
        lines = []
        for __ in range(args.sentences):
            speaker, line = chooser.random_dialog(speaker)
            lines.append(line)
        print_dialog(' '.join(set(lines)), speaker, args.attribute)
        if paragraph < args.paragraphs - 1:
            print()  # padding between paragraphs
