import contextlib
import json as _json
import logging
import os
import pickle as _pickle
import sqlite3

from ..backends.sqlite import DEFAULT_SQLITE_PATH
from ..scrape.utils import magicdictlist

logger = logging.getLogger(__name__)
writers = {}


def writer(fn):
    """Append function to available writers for the CLI."""
    writers[fn.__name__] = fn
    return fn


@writer
def raw(file_path, all_dialog, speakers=None, format='{speaker}:\n{line}\n\n', **kwargs):
    """Write raw text to file at specified path."""
    file_path = os.path.abspath(file_path)
    logger.info('dumping raw to %s', file_path)
    with open(file_path, 'w') as raw_file:
        for speaker, line in all_dialog:
            if not speakers or speaker in speakers:
                raw_file.write(format.format(speaker=speaker, line=line))


@writer
def json(file_path, dialog_dict, **kwargs):
    """Write json to file at specified path."""
    file_path = os.path.abspath(file_path)
    logger.info('dumping json to %s', file_path)
    with open(file_path, 'w') as json_file:
        _json.dump(dialog_dict, json_file, indent=4)


@writer
def sqlite(file_path, dialog_list, **kwargs):
    """Write sqlite db to file at specified path."""
    file_path = os.path.abspath(file_path)
    logger.info('dumping sqlite to %s', file_path)

    drop_sql = 'DROP TABLE IF EXISTS dialog'
    create_sql = 'CREATE TABLE IF NOT EXISTS dialog (' \
                 '  dialog_id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                 '  speaker VARCHAR,' \
                 '  line VARCHAR' \
                 ')'
    query = 'INSERT INTO dialog (speaker, line) VALUES (?,?)'
    index_sql = 'CREATE INDEX dialog_speaker_idx ON dialog(speaker)'

    with contextlib.closing(sqlite3.connect(file_path)) as conn, conn:
        conn.execute(drop_sql)
        conn.execute(create_sql)
        for speaker, line in dialog_list:
            # for line in lines:
            args = (speaker, line)
            conn.execute(query, args)
        conn.execute(index_sql)


@writer
def pickle(file_path, dialog_dict, **kwargs):
    """Write pickle to file at specified path."""
    file_path = os.path.abspath(file_path)
    logger.info('dumping pickle to %s', file_path)
    with open(file_path, 'wb') as pickle_file:
        _pickle.dump(dict(dialog_dict), pickle_file, protocol=2)  # 2 is py27-compatible


def write_assets(dialog_list):
    """Write to standard assets within the trekipsum package."""
    sqlite_path = DEFAULT_SQLITE_PATH
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
    sqlite(sqlite_path, dialog_list)


def dictify_dialog(all_dialog, speakers=None):
    """Group deduped lines of dialog by speaker into a dict."""
    dialog_dictset = magicdictlist()
    for speaker, line in all_dialog:
        if not speakers or speaker in speakers:
            dialog_dictset[speaker].append(line)
    return dialog_dictset.dedupe()
