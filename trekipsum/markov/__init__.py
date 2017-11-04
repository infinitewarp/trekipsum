import copy
import random
from collections import defaultdict


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
            if word[-1] == '.' and len(word.strip('.')) > 0:
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
            word = random.choice(self._chain.keys())
        else:
            if from_word not in self._chain:
                raise KeyError(from_word)
            target = random.random()
            total = 0.0
            for next_word, probability in self._chain[from_word]:
                word = next_word
                total += probability
                if probability >= target:
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
