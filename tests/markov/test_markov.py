import logging

from trekipsum import markov

logger = logging.getLogger(__name__)


def sort_probs(probs_list):
    """Sort probabilities list for consistent comparison."""
    return sorted(probs_list, key=lambda x: x[1])


def test_markov_word_chain_builder():
    """Test typical use of the WordChainBuilder markov chain class."""
    input_sequence = (
        'PIKARD', 'Q', 'PIKARD', 'DORF', 'PIKARD', 'Q', 'ROKER', 'Q', 'PIKARD'
    )
    expected_probabilities = {
        'PIKARD': [('Q', 2.0 / 3), ('DORF', 1.0 / 3)],
        'Q': [('PIKARD', 2.0 / 3), ('ROKER', 1.0 / 3)],
        'DORF': [('PIKARD', 1.0)],
        'ROKER': [('Q', 1.0)],
    }
    builder = markov.WordChainBuilder()
    for word in input_sequence:
        builder.add_next(word)
    chain = builder.normalize()

    for leader, probs in expected_probabilities.items():
        assert leader in chain
        assert sort_probs(probs) == sort_probs(chain[leader])


def test_markov_sentence_chain_builder_and_walker():
    """Test typical use of the SentenceChainBuilder markov chain class."""
    input_line = 'That would be illogical, Captain. There would be no profit.'
    expected_words = {
        'That', 'would', 'be', 'illogical,', 'Captain.',
        'There', 'no', 'profit.',
    }
    expected_first_words = {'That', 'There'}
    possible_phrases = {
        'That would be illogical, Captain.',
        'That would be no profit.',
        'There would be no profit.',
        'There would be illogical, Captain.',
    }
    builder = markov.SentenceChainBuilder()
    builder.process_string(input_line)
    chain = builder.normalize()

    for expected_word in expected_words:
        assert expected_word in chain
    assert len(chain) == len(expected_words) + 1  # plus EOL token

    for expected_word in expected_first_words:
        assert expected_word in (word for word, value in chain[''])
    assert len(chain['']) == len(expected_first_words)

    walker = markov.ChainWalker(chain)
    for _ in range(10):  # it's "good enough".
        sentence = walker.build_sentence()
        assert sentence in possible_phrases
