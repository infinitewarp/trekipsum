import random
from collections import defaultdict


class ChainNotNormalized(Exception):
    """Operation expects normalized chain but chain is not normalized."""


class ChainAlreadyNormalized(Exception):
    """Operation expects not normalized chain but chain is normalized."""


class WordChain(object):
    """Typical markov chain for words."""

    def __init__(self):
        """Initialize a new empty markov chain."""
        self._chain = defaultdict(lambda: defaultdict(lambda: 0))
        self._normalized = False
        self.__last_leader = None
        self.__last_generated = None

    def _expect_not_normalized(self):
        """Raise exception if chain is already normalized."""
        if self._normalized:
            raise ChainAlreadyNormalized()

    def _expect_normalized(self):
        """Raise exception if chain is not yet normalized."""
        if not self._normalized:
            raise ChainNotNormalized()

    def normalize(self):
        """
        Normalize the chain for generation.

        This has the side-effect of fundamentally changing the structure of
        self._chain from a dict of dicts to a dict of "pair" tuples.
        """
        self._expect_not_normalized()
        for leader, followers in self._chain.items():
            total = sum(followers.values())
            normalized_followers = list()
            for follower in followers.keys():
                norm_value = 1.0 * self._chain[leader][follower] / total
                normalized_followers.append((follower, norm_value))
            self._chain[leader] = normalized_followers
        self._normalized = True

    def add_link(self, leader, follower):
        """Add leader->follower relationship to the chain."""
        self._expect_not_normalized()
        self._chain[leader][follower] += 1
        self.__last_leader = leader

    def add_next(self, follower):
        """Add to the chain when the caller doesn't know the leader."""
        self._expect_not_normalized()
        if self.__last_leader is not None:
            self.add_link(self.__last_leader, follower)
        self.__last_leader = follower

    def generate_word(self, from_word=None):
        """Generate the next word from the markov chain."""
        self._expect_normalized()
        if from_word is None and self.__last_generated is None:
            word = random.choice(self._chain.keys())
        else:
            if from_word is None:
                from_word = self.__last_generated
            if from_word not in self._chain:
                raise KeyError(from_word)
            target = random.random()
            total = 0.0
            for next_word, probability in self._chain[from_word]:
                word = next_word
                total += probability
                if probability >= target:
                    break
        self.__last_generated = word
        return word


class SentenceChain(WordChain):
    """Markov chain with special logic to handle sentences."""

    _eol_token = ''  # magic value for beginning/ending a sentence

    def process_string(self, input_string):
        """Process the given string to add to the chain."""
        self._expect_not_normalized()
        words = input_string.split()
        last_word = self._eol_token
        for word in words:
            self.add_link(last_word, word)
            last_word = word
            if word[-1] == '.' and len(word.strip('.')) > 0:
                # specially handle word ending with period as end of sentence
                last_word = self._eol_token
                self.add_link(word, last_word)

        if last_word != self._eol_token:
            # ensure last word is end of sentence if not already
            self.add_link(last_word, self._eol_token)

    def generate_sentence(self):
        """Generate one sentence from the chain."""
        self._expect_normalized()
        last_word = self.generate_word(from_word=self._eol_token)
        words = list()
        while last_word != self._eol_token:
            words.append(last_word)
            last_word = self.generate_word(from_word=last_word)
        return ' '.join(words)
