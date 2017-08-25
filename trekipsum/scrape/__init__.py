import argparse
import json
import logging
import os
import pickle

import six

from .stminutiae import Scraper as STMScraper
from .utils import magicdictset

logger = logging.getLogger(__name__)


def parse_movies():
    """Parse movies scripts."""
    ids = [
        'tmp', 'twok', 'tsfs', 'tvh', 'tff', 'tuc', 'gens',
        # 'fc',  # first draft. *lots* of changes from final!
        'ins', 'nem',
    ]
    parsed_scripts = []
    scraper = STMScraper()
    for script_id in ids:
        parsed_scripts.append(scraper.parse_script(script_id))
    return parsed_scripts


def parse_tng():
    """Parse TNG scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    for script_id in range(102, 277 + 1):
        parsed_scripts.append(scraper.parse_script(script_id))
    return parsed_scripts


def parse_ds9():
    """Parse DS9 scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    for script_id in range(402, 575 + 1):
        parsed_scripts.append(scraper.parse_script(script_id))
    return parsed_scripts


def parse_voyager():
    """Parse Voyager scripts."""
    # TODO totally different format needs special treatment
    # one collection is http://chakoteya.net/Voyager/episode_listing.htm
    raise NotImplementedError()


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Script dialog scraper')
    parser.add_argument('-j', '--json', type=str, help='path to write json file')
    parser.add_argument('-p', '--pickle', type=str, help='path to write pickle file')

    types_group = parser.add_argument_group('include script sources')
    types_group.add_argument('--all', help='all', action='store_true')
    types_group.add_argument('--movies', help='movies', action='store_true')
    types_group.add_argument('--tng', help='the next generation', action='store_true')
    types_group.add_argument('--ds9', help='deep space nine', action='store_true')

    return parser.parse_args()


def main_cli():
    """Execute module as CLI program."""
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    args = parse_cli_args()

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
