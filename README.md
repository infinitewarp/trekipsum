# Trek Ipsum

[![License](https://img.shields.io/github/license/infinitewarp/trekipsum.svg)](https://github.com/infinitewarp/trekipsum/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/infinitewarp/trekipsum/master.svg)](https://travis-ci.org/infinitewarp/trekipsum)
[![Coveralls](https://img.shields.io/coveralls/infinitewarp/trekipsum/master.svg)](https://coveralls.io/github/infinitewarp/trekipsum)
[![Codecov](https://img.shields.io/codecov/c/github/infinitewarp/trekipsum.svg)](https://codecov.io/gh/infinitewarp/trekipsum/)
[![Requires.io](https://img.shields.io/requires/github/infinitewarp/trekipsum.svg)](https://requires.io/github/infinitewarp/trekipsum/requirements/?branch=master)
[![Codacy grade](https://img.shields.io/codacy/grade/39498999142242f2a2fb579aaf90241f/master.svg)](https://www.codacy.com/app/infinitewarp/trekipsum)

TrekIpsum is a command-line "lorem ipsum"-like text generator, powered by lines of dialog from the movies and TV series that make up the Star Trek multiverse.

Example usage:

    $ trekipsum
    'Aye, sir.' -- Saavik

    $ trekipsum
    "You're sure this is the right panel?" -- Sisko

    $ trekipsum --speaker riker --count 4 --no-attribute
    'Data, give us a visual. Magnfication factor fifty.'
    "I can't believe anything overtaking us this fast."
    'Can you correct for it?'
    'No questions. Just tell me a joke. The funniest joke in history.'


## First-time Setup

To side-step potential copyright infringement problems, TrekIpsum *does not include* in its distribution the actual dialog from the Star Trek miltiverse. However, since scripts have found their way onto the internet, TrekIpsum includes a `scrape` command that will fetch and parse the data from several online sources to populate a local database on your system.

To initialize the database, run the following command:

    python -m trekipsum.scrape --progress

This `scrape` command supports several other options if you wish to limit your database to particular sources (e.g. "only TNG scripts") or speakers (e.g. "only Spock dialog"). Use the `--help` argument for more details.
