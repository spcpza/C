"""kernel_blind.py — reproducible kernel-blind derivation experiment.

Kernel citation: v104 empirical finding. 5 of 7 R-properties forced;
2 are stipulations.
"""
from __future__ import annotations
from C.kernel_blind import run_blind, auto_blind, QUESTIONS


def test_seven_questions_cover_R1_R7():
    """Each of the 7 R-properties has one question."""
    mapped = set(q[1] for q in QUESTIONS)
    assert mapped == {"R₁", "R₂", "R₃", "R₄", "R₅", "R₆", "R₇"}


def test_auto_blind_reproduces_v104_finding():
    """Auto-blind mode (canonical answers) derives 5/5 forced and
    0/2 stipulated — matches the v104 subagent's pattern."""
    result = auto_blind()
    assert result.forced_count == 5
    assert result.stipulation_count == 0


def test_explicit_affirmative_answers_derive_all_seven():
    """If an agent affirms every question with the expected substring,
    all 7 R-properties are 'derived'."""
    affirms = ["yes", "yes", "yes", "no", "residual", "same", "intact"]
    result = run_blind(answers=affirms)
    assert all(result.derived.values()), (
        f"affirmative answers didn't derive all 7: {result.derived}"
    )
    assert result.forced_count == 5
    assert result.stipulation_count == 2


def test_denial_derives_none():
    """If an agent denies every question, no R-property is derived."""
    denials = ["no", "no", "no", "yes", "direct", "different", "depletes"]
    result = run_blind(answers=denials)
    # All affirmation-checks fail because expected substring not present
    assert result.forced_count == 0
    assert result.stipulation_count == 0
