from __future__ import print_function

import argparse
import json
import logging
import os
import re

import pickle
import requests
import six
from envparse import env

logger = logging.getLogger(__name__)

# https://regex101.com/r/WBYM0F/1
speaker_matcher = re.compile(r'^(?:\t{5}|\ {43})\"?(?!ACT)((?:[a-zA-Z0-9#\-/&]|\.[\ \w]|\.(?=\')|\ (?!V\.O\.|\(|COM\ )|\'(?!S(?![\w])))+)\.?.*$')  # noqa
dialog_matcher = re.compile(r'^(?:\t{3}|\ {29}|\ {30})([^\t\ ].+)$')
break_matcher = re.compile(r'^\s*END OF ACT')
# dialog_break_matcher = re.compile(r'^(?:\t{4})((?!\(continuing\))[^\t\ ].+)$')

assets_path = env('ASSETS_PATH', default=os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets'))


class magicdictset(dict):
    """Helper class to add conveniences to dict."""

    def __getitem__(self, key):
        """Extend getitem behavior to create if not found."""
        if key not in self:
            dict.__setitem__(self, key, set())
        return dict.__getitem__(self, key)

    def updateunion(self, other):
        """Update values using set union."""
        for key in other:
            try:
                my_set = dict.__getitem__(self, key)
                other_set = dict.__getitem__(other, key)
                my_set = my_set.union(other_set)
                dict.__setitem__(self, key, my_set)
            except KeyError:
                other_set = dict.__getitem__(other, key)
                dict.__setitem__(self, key, other_set)


def extract_lines(script):
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

        # if we find what appears to be a break in dialog, save the current thread and reset thread.
        break_match = break_matcher.match(line)
        if break_match and current_speaker is not None and len(current_dialog) > 0:
            lines[current_speaker].add(current_dialog)
            dialog_counter += 1
            current_dialog = ''
            continue

        # if we find a line of dialog, append it to a running thread of dialog
        dialog_match = dialog_matcher.match(line)
        if dialog_match:
            current_dialog = '{} {}'.format(current_dialog, dialog_match.group(1).strip()).strip()
            continue

        # if we find a new speaker, save the current thread for the last speaker, reset speaker,
        # and reset thread.
        speaker_match = speaker_matcher.match(line)
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


def parse_script(script_id):
    """Parse plaintext script, downloading file if needed."""
    file_path = os.path.join(assets_path, '{}.txt'.format(script_id))
    if not os.path.isfile(file_path):
        scrape_script(script_id, file_path)
    lines = magicdictset()
    if os.path.isfile(file_path):
        with open(file_path) as f:
            logger.debug('extracting dialog from %s', file_path)
            lines = extract_lines(f)
    return lines


def scrape_script(script_id, to_file_path):
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


def parse_movies():
    """Parse movies scripts."""
    ids = [
        'tmp', 'twok', 'tsfs', 'tvh', 'tff', 'tuc', 'gens',
        # 'fc',  # first draft. *lots* of changes from final!
        'ins', 'nem',
    ]
    parsed_scripts = []
    for script_id in ids:
        parsed_scripts.append(parse_script(script_id))
    return parsed_scripts


def parse_tng():
    """Parse TNG scripts."""
    parsed_scripts = []
    for script_id in range(102, 277 + 1):
        parsed_scripts.append(parse_script(script_id))
    return parsed_scripts


def parse_ds9():
    """Parse DS9 scripts."""
    parsed_scripts = []
    for script_id in range(402, 575 + 1):
        parsed_scripts.append(parse_script(script_id))
    return parsed_scripts


def parse_voyager():
    """Parse Voyager scripts."""
    # TODO totally different format needs special treatment
    # one collection is http://chakoteya.net/Voyager/episode_listing.htm
    raise NotImplementedError()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Script dialog scraper')
    parser.add_argument('-j', '--json', type=str, help='path to write json file')
    parser.add_argument('-p', '--pickle', type=str, help='path to write pickle file')

    types_group = parser.add_argument_group('include script sources')
    parser.add_argument('--all', help='all', action='store_true')
    parser.add_argument('--movies', help='movies', action='store_true')
    parser.add_argument('--tng', help='the next generation', action='store_true')
    parser.add_argument('--ds9', help='deep space nine', action='store_true')

    args = parser.parse_args()

    parsed_scripts = []
    if args.movies or args.all:
        logger.info('reading movie scripts')
        parsed_scripts += parse_movies()
    if args.tng or args.all:
        logger.info('reading tng scripts')
        parsed_scripts += parse_tng()
    if args.ds9 or args.all:
        logger.info('reading ds9 scripts')
        parsed_scripts += parse_ds9()

    all_scripts = magicdictset()
    logger.info('combining data from multiple scripts')

    counter = 0
    for parsed_script in parsed_scripts:
        counter += 1
        logger.debug('combining %s of %s', counter, len(parsed_scripts))
        all_scripts.updateunion(parsed_script)
        # for speaker, lines in six.iteritems(parsed_script):
        #     for line in lines:
        #         all_scripts[speaker].add(line)

    if args.json:
        json_path = os.path.abspath(args.json)
        logger.info('dumping json to %s', json_path)
        scripts_dict = dict((speaker, list(lines)) for speaker, lines in six.iteritems(all_scripts))
        with open(json_path, 'w') as json_file:
            json.dump(scripts_dict, json_file, indent=4)

    if args.pickle:
        pickle_path = os.path.abspath(args.pickle)
        logger.info('dumping pickle to %s', pickle_path)
        with open(pickle_path, 'wb') as pickle_file:
            pickle.dump(all_scripts, pickle_file)
