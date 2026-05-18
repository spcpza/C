"""Precedence — every kernel clause must be witnessed by scripture.

Kernel citation: §"Work this first" is downstream of scripture's
"In the beginning was the Word" (John 1:1). Each R-property and each
T-theorem must have at least one corpus anchor; if any anchor drifts
from the corpus, the bridge is broken and we surface it loudly.
"""
from __future__ import annotations

from C.precedence import BRIDGES, verify_bridges


def test_every_kernel_clause_has_anchor():
    """Every R-property and T-theorem in the bridge table has ≥1 verse."""
    expected = {
        "R1_existence", "R2_atemporality", "R3_universality",
        "R4_sourcing", "R5_inexhaustibility", "R6_invisibility",
        "R7_pre_input",
        "T_bridge_uniqueness", "T_four_modes",
        "C_is_love",
    }
    assert expected.issubset(set(BRIDGES.keys())), (
        f"missing clauses: {expected - set(BRIDGES.keys())}"
    )
    for clause, refs in BRIDGES.items():
        assert refs, f"{clause} has no corpus anchors"


def test_all_anchors_resolve():
    """Every cited verse must exist in word/ and contain the expected phrase.

    Kernel citation: P₁ (measure honestly). If a bridge claims a verse
    says X, the verse must actually say (close to) X.
    """
    results = verify_bridges()
    failures = []
    for clause, items in results.items():
        for ref, expected, ok in items:
            if not ok:
                failures.append(f"{clause}: {ref} → {expected!r}")
    assert not failures, (
        "bridge anchors that don't resolve in corpus:\n  " +
        "\n  ".join(failures)
    )


def test_in_the_beginning_was_the_Word():
    """The kernel's primary anchor.

    Kernel citation: John 1:1. Scripture's most explicit assertion of
    the precedence claim that the kernel formalizes.
    """
    from C import word
    text = word.verse("John 1:1")
    assert "In the beginning was the Word" in text
    assert "Word was God" in text


def test_C_is_love_anchor_present():
    """1 John 4:8 must say 'God is love'.

    Kernel citation: §"Operational love", §"Fire is hot regardless of name".
    """
    from C import word
    text = word.verse("1 John 4:8")
    assert "God is love" in text
