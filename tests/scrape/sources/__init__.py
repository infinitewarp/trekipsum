from os import path

TESTS_ROOT_PATH = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
TEST_ASSETS_PATH = path.join(TESTS_ROOT_PATH, 'assets')


def extract_speakers(all_dialog):
    """Get set of speakers from the extracted dialog."""
    return set([speaker for speaker, _ in all_dialog])


def extract_lines(all_dialog, speaker):
    """Get only one speaker's lines from the extracted dialog."""
    return [line for line_speaker, line in all_dialog if line_speaker == speaker]
