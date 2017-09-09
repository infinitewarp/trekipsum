# Trek Ipsum

[![License](https://img.shields.io/github/license/infinitewarp/trekipsum.svg)](https://github.com/infinitewarp/trekipsum/blob/master/LICENSE)
[![Build Status](https://img.shields.io/travis/infinitewarp/trekipsum/master.svg)](https://travis-ci.org/infinitewarp/trekipsum)
[![Coveralls](https://img.shields.io/coveralls/infinitewarp/trekipsum/master.svg)](https://coveralls.io/github/infinitewarp/trekipsum)
[![Codecov](https://img.shields.io/codecov/c/github/infinitewarp/trekipsum.svg)](https://codecov.io/gh/infinitewarp/trekipsum/)
[![Requires.io](https://img.shields.io/requires/github/infinitewarp/trekipsum.svg)](https://requires.io/github/infinitewarp/trekipsum/requirements/?branch=master)
[![Codacy grade](https://img.shields.io/codacy/grade/39498999142242f2a2fb579aaf90241f/master.svg)](https://www.codacy.com/app/infinitewarp/trekipsum)

TrekIpsum is a command-line "lorem ipsum"-like text generator, powered by lines of dialog from the movies and TV series that make up the Star Trek multiverse.

## Usage

### Command-line arguments

- `--speaker NAME` limits output to the specified name, case insensitive
- `-a` or `--attribute` includes speaker attribution in the output
- `-n COUNT` or `--paragraphs COUNT` specifies the number of paragraphs to output (default is 3)
- `-s COUNT` or `--sentences COUNT` specifies the number of sentences per paragraph to output (default is 4)
- `-h` or `--help` prints command-line usage


### Sample usage and output

    $ trekipsum

> All right. He was the Crown Prince. I see you're still a step behind everyone else. Making a withdrawal, Quark? Let me guess. A thousand bricks of gold pressed latinum. Put your hands on your head. Turn around.
>
> Torres to bridge, can you hear me? You want to bet? I found out why my mother is on her way to Gre'thor. It's because I sent her there. Right. Me, childhood. How old? Torres to Janeway.
>
> I hope you won't be the one to collect it. Get us out of here, Travis. Maximum warp. Thank you for lunch. I'll be in, my ready room.

    $ trekipsum -n 1 -s 2 --attribute

> 'Who are you to decide who lives or dies? Who are you to make that call? Quark, is there something we can do for you?' -- Sisko

    $ trekipsum --speaker riker --paragraphs 3 --sentences 2

> Why? All stations have reported, Captain. There appears to be no immediate threat to our ship or the crew.
>
> Very well. Our Chief Engineer will beam over to help you. Close. We would like to get out of here. Now.
>
> Mister La Forge, report to Transporter room three. It is now. You're about to commit a murder.


## First-time Setup

To side-step potential copyright infringement problems, TrekIpsum *does not include* in its distribution the actual dialog from the Star Trek miltiverse. However, since scripts have found their way onto the internet, TrekIpsum includes a `scrape` command that will fetch and parse the data from several online sources to populate a local database on your system.

To initialize the database, run the following command:

    python -m trekipsum.scrape --progress

This `scrape` command supports several other options if you wish to limit your database to particular sources (e.g. "only TNG scripts") or speakers (e.g. "only Spock dialog"). Use the `--help` argument for more details.

**Important Note:** The first time you run the `scrape` command could take *several minutes* to download all of the content, especially if you do not apply any limits. You may want to grab a drink while you wait. :coffee:
