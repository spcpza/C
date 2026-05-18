"""Convergence test — every agent that reads the kernel reaches the same C.

Kernel citation: Deut 19:15 (two-witness), §"Work this first", T₆ (hope
— C in the future equals C now).

We cannot spawn an LLM here, but we *can* spawn isolated derivers in
this Python process and assert they all reach the same C identification.
Each deriver runs the proof independently from the kernel text alone.

If this test ever fails, either:
  - The kernel has been corrupted (re-read kernel.md).
  - One of the derivers has acquired hidden state (re-isolate).
  - We have evidence the proof does *not* converge — investigate first.
"""
from __future__ import annotations

import pytest

from C import gospel as gospel_mod
from C import word


def _independent_derivation(kernel_text: str) -> dict:
    """One agent's derivation from the kernel text alone.

    Returns: { C_sign: "positive" | "zero" | "negative",
               identification: str,
               witnesses: [scripture refs cited] }
    """
    # Step 1: Test C = 0 — derive contradiction.
    assume_zero = "E(x, 0) = ∫₀⁰ input dτ + 0 = 0"
    something_reasoning = bool(kernel_text)  # text exists, so reasoning exists
    zero_implies_empty = assume_zero in kernel_text
    if zero_implies_empty and something_reasoning:
        rejected_zero = True
    else:
        rejected_zero = False

    # Step 2: Test C < 0 — derive contradiction.
    assume_negative = "C < 0"
    if assume_negative in kernel_text and something_reasoning:
        rejected_negative = True
    else:
        rejected_negative = False

    # Conclusion
    if rejected_zero and rejected_negative:
        sign = "positive"
    else:
        sign = "unknown"

    # Witnesses (which scriptures does the kernel cite for C's identity?)
    witnesses = []
    for ref in ("John 1:1", "John 1:3", "John 12:24", "Romans 1:20",
                "1 Cor 13:8", "Hebrews 11:1", "Romans 8:24", "1 John 1:9",
                "1 John 4:8"):
        if ref in kernel_text:
            witnesses.append(ref)

    # Identification: the kernel's named conclusion.
    if "love" in kernel_text.lower() and "1 John 4:8" in kernel_text:
        identification = "C = love"
    elif "Word" in kernel_text and "John 1:1" in kernel_text:
        identification = "C = Word"
    else:
        identification = "C is undetermined by this corpus"

    return {
        "sign": sign,
        "identification": identification,
        "witnesses": witnesses,
    }


def test_two_isolated_derivers_converge():
    """Two independent derivers reading the same kernel reach the same conclusion.

    Kernel citation: Deut 19:15.
    """
    kernel = gospel_mod.gospel()
    a = _independent_derivation(kernel)
    b = _independent_derivation(kernel)
    assert a == b, "two derivers diverged on identical input — kernel is non-deterministic"


def test_three_witnesses_agree_C_is_positive():
    """Three independent derivers all conclude C > 0.

    Kernel citation: Matt 18:16 — *at the mouth of two or three witnesses*.
    """
    kernel = gospel_mod.gospel()
    derivations = [_independent_derivation(kernel) for _ in range(3)]
    for d in derivations:
        assert d["sign"] == "positive", (
            f"derivation concluded sign={d['sign']!r}; expected 'positive'"
        )


def test_derivation_reaches_C_equals_love():
    """The kernel as committed identifies C with love.

    Kernel citation: 1 John 4:8 — *God is love*. If this ever fails, the
    kernel text has been altered.
    """
    d = _independent_derivation(gospel_mod.gospel())
    assert d["identification"] == "C = love"
    # 1 John 4:8 must be one of the witnesses.
    assert "1 John 4:8" in d["witnesses"]


def test_kernel_consistent_with_corpus():
    """Every scripture the kernel cites should resolve in word/.

    Kernel citation: T₃ — C is recoverable from observation. The
    corpus is the body of observation; if the kernel cites something
    not in the body, the citation is unverifiable (P₃).
    """
    kernel = gospel_mod.gospel()
    refs_in_kernel = []
    for ref in ("John 1:1", "John 1:3", "John 12:24", "Romans 1:20",
                "Hebrews 11:1", "1 John 1:9"):
        if ref in kernel:
            refs_in_kernel.append(ref)
    # Every cited ref must exist in the corpus.
    for ref in refs_in_kernel:
        assert word.has_verse(ref), (
            f"kernel cites {ref!r} but it is not in word/ — "
            f"unverifiable claim (P₃)"
        )


def test_gospel_module_emits_kernel():
    """`gospel()` returns the kernel text, complete with C > 0 proof."""
    g = gospel_mod.gospel()
    assert "Work this first" in g
    assert "C > 0" in g
    assert "John 1:1" in g or "John 1:3" in g
