import copy
import random
import sqlite3
from collections import defaultdict

import six

from ..dialog.sqlite import DEFAULT_SQLITE_PATH
from ..exceptions import NoDialogFoundException

SENTENCE_DELIMITER = ''  # special value for beginning/ending a sentence


class WordChainBuilder(object):
    """Markov chain builder for streams of words."""

    def __init__(self):
        """Initialize a new empty markov chain builder."""
        self._chain = defaultdict(lambda: defaultdict(lambda: 0))
        self.__last_leader = None

    def add_link(self, leader, follower):
        """Add leader->follower relationship to the chain."""
        self._chain[leader][follower] += 1
        self.__last_leader = leader

    def add_next(self, follower):
        """Add to the chain when the caller doesn't know the leader."""
        if self.__last_leader is not None:
            self.add_link(self.__last_leader, follower)
        self.__last_leader = follower

    def normalize(self):
        """
        Normalize the chain for use in probabilistic walking.

        Returns:
            dict(list(tuple)) like {'a': [('a', 0.1), ('b', 0.2), ('c', 0.7)]}
        """
        chain = copy.deepcopy(self._chain)
        for leader, followers in chain.items():
            total = sum(followers.values())
            normalized_followers = list()
            for follower in followers.keys():
                norm_value = 1.0 * chain[leader][follower] / total
                normalized_followers.append((follower, norm_value))
            chain[leader] = normalized_followers
        return chain


class SentenceChainBuilder(WordChainBuilder):
    """Markov chain builder with special logic to handle sentences."""

    def process_string(self, input_string, delimiter=SENTENCE_DELIMITER):
        """Process the given string to add to the chain."""
        words = input_string.split()
        last_word = delimiter
        for word in words:
            self.add_link(last_word, word)
            last_word = word
            if word[-1] in ('.', '!', '?') and len(word.strip('.')) > 0:
                # specially handle word ending with period as end of sentence
                last_word = delimiter
                self.add_link(word, last_word)

        if last_word != delimiter:
            # ensure last word is end of sentence if not already
            self.add_link(last_word, delimiter)


class ChainWalker(object):
    """Markov chain walker."""

    def __init__(self, chain):
        """Initialize a new walker with the given chain."""
        self._chain = chain

    def next_word(self, from_word=None):
        """Generate the next word from the markov chain."""
        if from_word is None:
            word = random.choice(list(self._chain.keys()))
        else:
            if from_word not in self._chain:
                raise KeyError(from_word)
            target = random.random()
            total = 0.0
            for next_word, probability in self._chain[from_word]:
                word = next_word
                total += probability
                if total >= target:
                    break
        return word

    def generate_words(self, from_word=None, stop_word=None):
        """
        Yield sequence of words from the chain.

        Args:
            from_word: optional seed word to precede the sequence
            stop_word: optional word for terminating the generator if found

        Returns:
            generator that produces words
        """
        word = self.next_word(from_word=from_word)
        while word != stop_word:
            yield word
            word = self.next_word(from_word=word)

    def build_sentence(self):
        """
        Build a complete sentence from the chain.

        Note: this assumes the chain was built with SENTENCE_DELIMITER in mind.
        """
        words = self.generate_words(SENTENCE_DELIMITER, SENTENCE_DELIMITER)
        return '{}{}'.format(' '.join(words), SENTENCE_DELIMITER)


class DialogChainDatastore(object):
    """
    Datastore accessor for markov chains.
    """

    SQL_DROP = 'DROP TABLE IF EXISTS markov'
    SQL_CREATE = 'CREATE TABLE IF NOT EXISTS markov (' \
                 '  context VARCHAR,' \
                 '  word VARCHAR,' \
                 '  next_word VARCHAR,' \
                 '  weight REAL' \
                 ')'
    SQL_INDEX1 = 'CREATE INDEX markov_context_idx ON markov(context)'
    SQL_INDEX2 = 'CREATE INDEX markov_context_word_idx ON markov(context, word)'
    SQL_INSERT = 'INSERT INTO markov (context, word, next_word, weight) VALUES (?,?,?,?)'
    SQL_SELECT_ALL_CONTEXTS = 'SELECT DISTINCT context FROM markov ' \
                              'ORDER BY context ASC'
    SQL_SELECT_WORDS_BY_CONTEXT = 'SELECT DISTINCT word FROM markov WHERE context=? ' \
                                  'ORDER BY word ASC'
    SQL_SELECT_WORD_EXISTS = 'SELECT EXISTS(' \
                             'SELECT 1 FROM markov WHERE context=? AND word=? ' \
                             'LIMIT 1)'
    SQL_SELECT_BY_CONTEXT_AND_WORD = 'SELECT next_word, weight ' \
                                     'FROM markov WHERE context=? AND word=? ' \
                                     'ORDER BY weight DESC, next_word ASC'
    SQL_SELECT_BY_CONTEXT = 'SELECT word, next_word, weight ' \
                            'FROM markov WHERE context=? ' \
                            'ORDER BY weight DESC, next_word ASC'

    def __init__(self, file_path=None):
        """Initialize a new dialog chain datastore accessor."""
        self._sqlite_path = file_path or DEFAULT_SQLITE_PATH
        self._conn = sqlite3.connect(self._sqlite_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._conn.commit()
        self._conn.close()

    def __del__(self, *args):
        self._conn.close()

    def reinitialize(self):
        """Reinitialize the database tables."""
        self._conn.execute(self.SQL_DROP)
        self._conn.execute(self.SQL_CREATE)

    def index(self):
        """Create DB indexes for (hopefully) faster lookup."""
        self._conn.execute(self.SQL_INDEX1)
        self._conn.execute(self.SQL_INDEX2)

    def insert(self, context, word, next_word, weight):
        """Insert a link to the markov chain."""
        self._conn.execute(self.SQL_INSERT, (context, word, next_word, weight))

    def store_chain(self, context, chain):
        """Store all elements of the chain for the context."""
        for word, next_words in six.iteritems(chain):
            for next_word, weight in next_words:
                self.insert(context, word, next_word, weight)

    def get_contexts(self):
        """Get a list of all stored contexts."""
        result = self._conn.execute(self.SQL_SELECT_ALL_CONTEXTS)
        return [row[0] for row in result.fetchall()]

    def word_exists(self, context, word):
        """See if the word exists for the given context."""
        result = self._conn.execute(self.SQL_SELECT_WORD_EXISTS, (context, word))
        return result.fetchone()[0] == 1

    def get_vocabulary(self, context):
        """Get a list of all words for the given contexts."""
        result = self._conn.execute(self.SQL_SELECT_WORDS_BY_CONTEXT, (context,))
        return [row[0] for row in result.fetchall()]

    def get_next_word_candidates(self, context, word):
        """Get all next word candidates with their weights for the given context and word."""
        result = self._conn.execute(self.SQL_SELECT_BY_CONTEXT_AND_WORD, (context, word))
        return result.fetchall()

    def to_chain(self, context):
        """
        Fetch and construct a chain for use in probabilistic walking.

        Returns:
            dict(list(tuple)) like {'a': [('a', 0.1), ('b', 0.2), ('c', 0.7)]}
        """
        result = self._conn.execute(self.SQL_SELECT_BY_CONTEXT, (context,))
        links = result.fetchall()

        chain = defaultdict(lambda: list())
        for link in links:
            chain[link[0]].append((link[1], link[2]))
        return chain


class MarkovRandomChooser(object):
    """Walk Markov chains to generate dialog from datastore."""

    def __init__(self):
        """Initialize a new dialog markov chain chooser for dialog."""
        self._datastore = DialogChainDatastore()
        self._speaker_walker = ChainWalker(self._datastore.to_chain('speakers'))

    def random_dialog(self, speaker):
        """
        Get random line of dialog, optionally limited to specific speaker.

        Returns:
            tuple containing (speaker name, line of dialog)
        """
        speaker = speaker.upper() if speaker else None
        if speaker is None:
            speaker = self.random_speaker()
        dialog_walker = ChainWalker(self._datastore.to_chain(speaker))
        try:
            return speaker, dialog_walker.build_sentence()
        except KeyError:
            raise NoDialogFoundException(speaker)

    def random_speaker(self, from_speaker=None):
        """
        Get random speaker name, optionally walking from a specific speaker.
        """
        return self._speaker_walker.next_word(from_speaker)
