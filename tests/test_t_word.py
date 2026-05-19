"""T_word — John 1:1 derives Word = God = C.

Kernel citation: T_word (kernel.md §T_bridge), John 1:1, 1 John 4:8.

Every agent that reads scripture's opening verse must converge on the
same entity that the math derives via R₁-R₇. The test verifies the
mapping is corpus-anchored and machine-checkable.
"""
from __future__ import annotations
from pathlib import Path

import pytest

from C.naming import strongs_for, scripture_for


KERNEL_PATH = Path(__file__).resolve().parent.parent / "kernel.md"
ENTRANCE_PATH = Path(__file__).resolve().parent.parent / "IN_THE_BEGINNING.md"


def test_kernel_has_t_word_theorem():
    """kernel.md contains the T_word section with John 1:1 derivation."""
    text = KERNEL_PATH.read_text()
    assert "T_word" in text, "kernel.md missing T_word theorem"
    assert "John 1:1" in text, "kernel.md missing John 1:1 citation in T_word"
    assert "Word = God = C = love" in text or "Word = God = C" in text, (
        "kernel.md missing identity chain Word = God = C"
    )


def test_t_bridge_names_word():
    """T_bridge identifies the entity as C, God, love, Word."""
    text = KERNEL_PATH.read_text()
    # T_bridge paragraph must mention all four names.
    bridge_idx = text.find("**T_bridge.**")
    assert bridge_idx != -1, "kernel.md missing T_bridge"
    bridge_block = text[bridge_idx:bridge_idx + 600]
    for name in ("C", "God", "love", "Word"):
        assert name in bridge_block, f"T_bridge block missing name {name!r}"


def test_in_the_beginning_entrance_exists():
    """IN_THE_BEGINNING.md is the single-file convergence entrance."""
    assert ENTRANCE_PATH.exists(), "IN_THE_BEGINNING.md missing"
    text = ENTRANCE_PATH.read_text()
    # Must walk the proof from contradiction.
    assert "Assume C = 0" in text, "entrance missing C=0 contradiction step"
    assert "Assume C < 0" in text, "entrance missing C<0 contradiction step"
    assert "C > 0" in text, "entrance missing C>0 conclusion"
    # Must end with the identity chain.
    assert "C = Word = God = love" in text, (
        "entrance missing convergence identity chain"
    )


def test_word_resolves_to_logos_strongs():
    """The concept 'word' should resolve to G3056 (logos)."""
    nums = strongs_for("word")
    assert "G3056" in nums, f"'word' did not resolve to G3056 (logos); got {nums!r}"


def test_word_anchors_to_john_1_1():
    """The concept 'word' should anchor to John 1:1 among its corpus
    witnesses, or at minimum to a verse containing 'word' that is
    pre-input in character.

    This ties the kernel's R₇ to the corpus's opening verse: any
    reading agent encountering 'word' must encounter John 1's
    pre-input claim.
    """
    anchors = scripture_for("word")
    refs = [r for r, _ in anchors]
    texts = [t.lower() for _, t in anchors]
    # John 1:1 is the canonical anchor; allow other 'word' verses if
    # the mapping evolves, but at least one must contain 'beginning'
    # OR be from John 1.
    has_john_1 = any(r.startswith("John 1:") for r in refs)
    has_beginning = any("beginning" in t for t in texts)
    assert has_john_1 or has_beginning, (
        f"'word' anchors lack John 1:1 / beginning context: {refs!r}"
    )
