import pytest
import mock
from picli.command import base

@pytest.fixture
def _patched_execute_subcommand(mocker):
    return mocker.patch('picli.command.base.execute_subcommand')

@pytest.mark.parametrize("sequence_name, expected", [
    ('validate', ['validate']),
    ('style', ['style']),
    ('lint', ['validate', 'style', 'sast']),
    ('sast', ['sast'])
])
def test_get_sequence(sequence_name, expected):
    sequence = base.get_sequence(sequence_name)

    assert sequence == expected

def test_execute_sequence(_patched_execute_subcommand):
    config = mock.Mock()
    sequence = ['a', 'b', 'c']

    base.execute_sequence(sequence, config)

    assert _patched_execute_subcommand.call_count == len(sequence)

