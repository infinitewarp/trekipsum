import tqdm

sources = {}


def source(fn):
    """Append function to available sources for the CLI."""
    sources[fn.__name__] = fn
    return fn


def _scrape_ids(ids, scraper, name, progress=False):
    parsed_scripts = []
    iterator = tqdm.tqdm(ids, 'Processing {} scripts'.format(name)) if progress else ids
    for script_id in iterator:
        parsed_scripts += scraper.extract_dialog(script_id)
    return parsed_scripts


@source
def tos(module, progress=False):
    """Include the original series TV scripts."""
    return _scrape_ids(module.ids['tos'], module.Scraper(), 'original', progress)


@source
def tas(module, progress=False):
    """Include the animated series TV scripts."""
    return _scrape_ids(module.ids['tas'], module.Scraper(), 'animated', progress)


@source
def tng(module, progress=False):
    """Include The Next Generation TV scripts."""
    return _scrape_ids(module.ids['tng'], module.Scraper(), 'TNG', progress)


@source
def ds9(module, progress=False):
    """Include Deep Space Nine TV scripts."""
    return _scrape_ids(module.ids['ds9'], module.Scraper(), 'DS9', progress)


@source
def voy(module, progress=False):
    """Include Voyager TV scripts."""
    return _scrape_ids(module.ids['voy'], module.Scraper(), 'Voyager', progress)


@source
def ent(module, progress=False):
    """Include Enterprise TV scripts."""
    return _scrape_ids(module.ids['ent'], module.Scraper(), 'Enterprise', progress)


@source
def mov_tos(module, progress=False):
    """Include TOS-era movie scripts."""
    return _scrape_ids(module.ids['mov_tos'], module.Scraper(), 'TOS movies', progress)


@source
def mov_tng(module, progress=False):
    """Include TNG-era movie scripts."""
    return _scrape_ids(module.ids['mov_tng'], module.Scraper(), 'TNG movies', progress)


# @source  # not yet ready
# def mov_jja(progress=False):
#     """Include JJ Abrams-verse movie scripts."""
#     raise NotImplementedError()
