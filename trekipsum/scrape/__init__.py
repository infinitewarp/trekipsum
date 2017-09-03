import argparse
import contextlib
import json
import logging
import os
import pickle
import sqlite3
import sys

import six
import tqdm

from .. import SQLITE_ASSETS_PATH
from .stminutiae import Scraper as STMScraper
from .utils import magicdictlist

logger = logging.getLogger(__name__)

LOG_FORMAT_BASIC = '%(levelname)s: %(message)s'
LOG_FORMAT_NOISY = '%(asctime)s %(levelname)s: %(message)s'


def parse_movies(progress=False):
    """Parse movies scripts."""
    ids = [
        'tmp', 'twok', 'tsfs', 'tvh', 'tff', 'tuc', 'gens',
        # 'fc',  # first draft. *lots* of changes from final!
        'ins', 'nem',
    ]
    parsed_scripts = []
    scraper = STMScraper()
    iterator = tqdm.tqdm(ids, 'Processing movie scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


def parse_tng(progress=False):
    """Parse TNG scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    ids = tuple(range(102, 277 + 1))
    iterator = tqdm.tqdm(ids, 'Processing TNG scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


def parse_ds9(progress=False):
    """Parse DS9 scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    ids = tuple(range(402, 472 + 1)) + tuple(range(474, 575 + 1))
    iterator = tqdm.tqdm(ids, 'Processing DS9 scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


def parse_voyager():
    """Parse Voyager scripts."""
    # TODO totally different format needs special treatment
    # one collection is http://chakoteya.net/Voyager/episode_listing.htm
    raise NotImplementedError()


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Script dialog scraper')
    parser.add_argument('--no-assets', help='do not write trekipsum module assets',
                        action='store_true')
    parser.add_argument('--speakers', type=str, nargs='+', help='limit output to these speakers')

    types_group = parser.add_argument_group('include script sources')
    types_group.add_argument('--all', help='all', action='store_true')
    types_group.add_argument('--movies', help='movies', action='store_true')
    types_group.add_argument('--tng', help='the next generation', action='store_true')
    types_group.add_argument('--ds9', help='deep space nine', action='store_true')

    dump_group = parser.add_argument_group('additional custom output')
    dump_group.add_argument('-j', '--json', type=str, help='path to write json file')
    dump_group.add_argument('-p', '--pickle', type=str, help='path to write pickle file')
    dump_group.add_argument('-r', '--raw', type=str, help='path to write raw, unoptimized scripts')
    dump_group.add_argument('-s', '--sqlite', type=str, help='path to write sqlite db')

    additional_group = parser.add_argument_group('additional arguments')
    additional_group.add_argument('--progress', action='store_true', help='show progress bars')
    additional_group.add_argument('-v', '--verbose', action='count', default=0,
                                  help='verbose mode; multiple -v options increase the verbosity')

    return parser.parse_args()


def configure_logging(verbosity):
    """
    Configure logging based on requested verbosity level.

    0 displays warning messages
    1 displays info messages
    2 display debug messages and includes timestamp
    """
    if verbosity == 0:
        log_level = logging.WARNING
    elif verbosity == 1:
        log_level = logging.INFO
    elif verbosity > 1:
        log_level = logging.DEBUG

    if verbosity <= 1:
        log_format = LOG_FORMAT_BASIC
    elif verbosity > 1:
        log_format = LOG_FORMAT_NOISY

    logging.basicConfig(level=log_level, format=log_format)
    logger.setLevel(log_level)


def main_cli():
    """Execute module as CLI program."""
    args = parse_cli_args()

    configure_logging(args.verbose)

    if not any((not args.no_assets, args.json, args.pickle, args.sqlite, args.raw)):
        logger.error('Nothing to do; no outputs specified.')
        sys.exit(1)

    all_dialog = []
    if args.movies or args.all:
        logger.info('reading movie scripts')
        all_dialog += parse_movies(args.progress)
    if args.tng or args.all:
        logger.info('reading tng scripts')
        all_dialog += parse_tng(args.progress)
    if args.ds9 or args.all:
        logger.info('reading ds9 scripts')
        all_dialog += parse_ds9(args.progress)

    if args.json or args.pickle or args.sqlite or not args.no_assets:
        dialog_dict = _dictify_dialog(all_dialog, args.speakers)

    if not args.no_assets:
        _write_assets(dialog_dict)

    if args.raw:
        _write_raw(args.raw, all_dialog, args.speakers)

    if args.json:
        _write_json(args.json, dialog_dict)

    if args.pickle:
        _write_pickle(args.pickle, dialog_dict)

    if args.sqlite:
        _write_sqlite(args.sqlite, dialog_dict)


def _write_raw(raw_path, all_dialog, speakers=None, format='{speaker}:\n{line}\n\n'):
    raw_path = os.path.abspath(raw_path)
    logger.info('dumping raw to %s', raw_path)
    with open(raw_path, 'w') as raw_file:
        for speaker, line in all_dialog:
            if not speakers or speaker in speakers:
                raw_file.write(format.format(speaker=speaker, line=line))


def _dictify_dialog(all_dialog, speakers=None):
    dialog_dictset = magicdictlist()
    for speaker, line in all_dialog:
        if not speakers or speaker in speakers:
            dialog_dictset[speaker].append(line)
    return dialog_dictset.dedupe()


def _write_json(json_path, dialog_dict):
    json_path = os.path.abspath(json_path)
    logger.info('dumping json to %s', json_path)
    with open(json_path, 'w') as json_file:
        json.dump(dialog_dict, json_file, indent=4)


def _write_pickle(pickle_path, dialog_dict):
    pickle_path = os.path.abspath(pickle_path)
    logger.info('dumping pickle to %s', pickle_path)
    with open(pickle_path, 'wb') as pickle_file:
        pickle.dump(dict(dialog_dict), pickle_file, protocol=2)  # 2 is py27-compatible


def _write_assets(dialog_dict):
    sqlite_path = SQLITE_ASSETS_PATH
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
    _write_sqlite(sqlite_path, dialog_dict)


def _write_sqlite(sqlite_path, dialog_dict):
    sqlite_path = os.path.abspath(sqlite_path)
    logger.info('dumping sqlite to %s', sqlite_path)

    drop_sql = 'DROP TABLE IF EXISTS dialog'
    create_sql = 'CREATE TABLE IF NOT EXISTS dialog (' \
                 '  dialog_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                 '  speaker VARCHAR,' \
                 '  line VARCHAR' \
                 ')'
    query = 'INSERT INTO dialog (speaker, line) VALUES (?,?)'
    index_sql = 'CREATE INDEX dialog_speaker_idx ON dialog(speaker)'

    with contextlib.closing(sqlite3.connect(sqlite_path)) as conn, conn:
        conn.execute(drop_sql)
        conn.execute(create_sql)
        for speaker, lines in six.iteritems(dialog_dict):
            for line in lines:
                args = (speaker, line)
                conn.execute(query, args)
        conn.execute(index_sql)
