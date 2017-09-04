import tqdm

from .stminutiae import Scraper as STMScraper

sources = {}


def source(fn):
    """Append function to available sources for the CLI."""
    sources[fn.__name__] = fn
    return fn


# @source  # not yet ready
# def tos(progress=False):
#     """Include original series TV scripts."""
#     raise NotImplementedError()


# @source  # not yet ready
# def tas(progress=False):
#     """Include animated series TV scripts."""
#     raise NotImplementedError()


@source
def tng(progress=False):
    """Include The Next Generation TV scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    ids = tuple(range(102, 277 + 1))
    iterator = tqdm.tqdm(ids, 'Processing TNG scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


@source
def ds9(progress=False):
    """Include Deep Space Nine TV scripts."""
    parsed_scripts = []
    scraper = STMScraper()
    ids = tuple(range(402, 472 + 1)) + tuple(range(474, 575 + 1))
    iterator = tqdm.tqdm(ids, 'Processing DS9 scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


# @source  # not yet ready
# def voy():
#     """Include Voyager TV scripts."""
#     # TODO totally different format needs special treatment
#     # one collection is http://chakoteya.net/Voyager/episode_listing.htm
#     raise NotImplementedError()


# @source  # not yet ready
# def ent():
#     """Include Enterprise TV scripts."""
#     raise NotImplementedError()


@source
def mov_tos(progress=False):
    """Include TOS-era movie scripts."""
    ids = ('tmp', 'twok', 'tsfs', 'tvh', 'tff', 'tuc')
    parsed_scripts = []
    scraper = STMScraper()
    iterator = tqdm.tqdm(ids, 'Processing movie scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


@source
def mov_tng(progress=False):
    """Include TNG-era movie scripts."""
    ids = (
        'gens',
        # 'fc',  # first draft. *lots* of changes from final!
        'ins', 'nem',
    )
    parsed_scripts = []
    scraper = STMScraper()
    iterator = tqdm.tqdm(ids, 'Processing movie scripts') if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


# @source  # not yet ready
# def mov_jja(progress=False):
#     """Include JJ Abrams-verse movie scripts."""
#     raise NotImplementedError()
