"""The interactive walk converges to C = love when the answers are right."""
from __future__ import annotations

from C.gospel_walk import walk, auto_derive, STEPS


def test_correct_answers_converge():
    result = walk(answers=[
        "non-empty",
        "cannot reason",
        "positive",
        "the Word",
        "love",
    ])
    assert result.converged
    assert result.failed_step is None
    assert len(result.transcript) == len(STEPS)


def test_wrong_answer_fails_at_step():
    result = walk(answers=[
        "non-empty",
        "yes it can",        # wrong
        "positive",
        "the Word",
        "love",
    ])
    assert not result.converged
    assert result.failed_step == 1


def test_auto_derive_succeeds():
    """The scripted self-derivation always converges."""
    result = auto_derive()
    assert result.converged
