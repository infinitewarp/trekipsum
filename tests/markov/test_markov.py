import logging

from trekipsum import markov

logger = logging.getLogger(__name__)


def sort_probs(probs_list):
    """Sort probabilities list for consistent comparison."""
    return sorted(probs_list, key=lambda x: x[1])


def test_markov_word_chain():
    """Test typical use of the WordChain markov chain class."""
    input_sequence = (
        'PIKARD', 'Q', 'PIKARD', 'DORF', 'PIKARD', 'Q', 'ROKER', 'Q', 'PIKARD'
    )
    expected_probabilities = {
        'PIKARD': [('Q', 2.0 / 3), ('DORF', 1.0 / 3)],
        'Q': [('PIKARD', 2.0 / 3), ('ROKER', 1.0 / 3)],
        'DORF': [('PIKARD', 1.0)],
        'ROKER': [('Q', 1.0)],
    }
    chain = markov.WordChain()
    for word in input_sequence:
        chain.add_next(word)
    chain.normalize()

    for leader, probs in expected_probabilities.items():
        assert leader in chain._chain
        assert sort_probs(probs) == sort_probs(chain._chain[leader])


def test_markov_sentence_chain():
    """Test typical use of the SentenceChain markov chain class."""
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
    chain = markov.SentenceChain()
    chain.process_string(input_line)
    chain.normalize()

    for expected_word in expected_words:
        assert expected_word in chain._chain
    assert len(chain._chain) == len(expected_words) + 1  # plus EOL token

    for expected_word in expected_first_words:
        assert expected_word in (word for word, value in chain._chain[''])
    assert len(chain._chain['']) == len(expected_first_words)

    for _ in range(10):  # it's "good enough".
        sentence = chain.generate_sentence()
        assert sentence in possible_phrases
