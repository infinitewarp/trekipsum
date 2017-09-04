from __future__ import print_function

import argparse
import logging

from trekipsum import backends

logger = logging.getLogger(__name__)


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='TrekIpsum generator')
    parser.add_argument('--speaker', type=str, help='limit output to this speakers')
    parser.add_argument('--no-attribute', help='hide speaker attribution', action='store_true')
    parser.add_argument('--count', type=int, default=1, help='lines of dialog to output')
    parser.add_argument('--debug', help='enable debug logging', action='store_true')

    advanced_group = parser.add_argument_group('experimental options')
    advanced_group.add_argument('--sqlite', action='store_true', help='use sqlite processor')
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
    if args.sqlite:
        chooser = backends.SqliteRandomChooser(speaker=args.speaker)
    else:
        chooser = backends.PickleRandomChooser(speaker=args.speaker)
    for _ in range(args.count):
        speaker, line = chooser.random_dialog()
        print_dialog(line, speaker, not args.no_attribute)
