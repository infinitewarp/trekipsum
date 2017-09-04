import argparse
import inspect
import logging
import sys

import six

from .sources import sources
from .writers import dictify_dialog, write_assets, writers

logger = logging.getLogger(__name__)

LOG_FORMAT_BASIC = '%(levelname)s: %(message)s'
LOG_FORMAT_NOISY = '%(asctime)s %(levelname)s: %(message)s'


def doc_headline(fn):
    """Get the first line of the specified function's docstring."""
    return inspect.getdoc(fn).split('\n')[0]


def parse_cli_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Script dialog scraper')
    parser.add_argument('--no-assets', help='do not write trekipsum module assets',
                        action='store_true')
    parser.add_argument('--speakers', type=str, nargs='+', help='limit output to these speakers')

    source_group = parser.add_argument_group('If specified, limit source data to')
    for name, source in six.iteritems(sources):
        source_group.add_argument('--{}'.format(name), action='store_true',
                                  help=doc_headline(source))

    output_group = parser.add_argument_group('Additional optional files to write')
    for name, writer in six.iteritems(writers):
        output_group.add_argument('--{}'.format(name), type=str,
                                  help=doc_headline(writer))

    additional_group = parser.add_argument_group('CLI display options')
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

    enabled_sources = [source for name, source in six.iteritems(sources)
                       if getattr(args, name)]
    if len(enabled_sources) == 0:
        enabled_sources = sources.values()
        logger.debug('No sources specified; defaulting to scrape all.')

    enabled_writers = [(writer, getattr(args, name))
                       for name, writer in six.iteritems(writers)
                       if getattr(args, name)]

    if args.no_assets and len(enabled_writers) == 0:
        logger.error('Nothing to do; no outputs specified.')
        sys.exit(1)

    all_dialog = read_sources(enabled_sources, args.progress)
    write_outputs(all_dialog, args.no_assets, enabled_writers, args.speakers)


def read_sources(enabled_sources, progress):
    """Read from all enabled sources and return all combined dialog."""
    all_dialog = []
    for source in enabled_sources:
        all_dialog += source(progress)
    return all_dialog


def write_outputs(all_dialog, no_assets=False, enabled_writers=(), speakers=()):
    """Write to all enabled writers."""
    if not no_assets:
        write_assets(all_dialog)

    if len(enabled_writers) > 0:
        dialog_dict = dictify_dialog(all_dialog, speakers)
        kwargs = {
            'dialog_dict': dialog_dict,
            'dialog_list': all_dialog,
            'speakers': speakers,
        }
        for writer, file_path in enabled_writers:
            kwargs['file_path'] = file_path
            writer(**kwargs)
