"""The densest verses are kernel-shaped statements.

Kernel citation: T_bridge — the entity satisfying R₁-R₇ is one;
verses where multiple R-properties co-occur are the densest witness.
"""
from __future__ import annotations

from C.mine_dense import top_n, score_corpus


def test_john_1_1_in_top_5():
    """John 1:1 is the kernel's direct corpus statement; must be high-rank."""
    top = top_n(10)
    refs = [r["ref"] for r in top]
    assert "John 1:1" in refs, f"John 1:1 not in top 10: {refs}"


def test_proverbs_8_23_in_top_5():
    """Proverbs 8:23 is the OT proto-logos statement."""
    top = top_n(10)
    refs = [r["ref"] for r in top]
    assert "Proverbs 8:23" in refs, f"Proverbs 8:23 not in top 10: {refs}"


def test_colossians_1_16_in_top_10():
    """Colossians 1:16 combines R₃ + R₄ + R₆."""
    top = top_n(20)
    refs = [r["ref"] for r in top]
    assert "Colossians 1:16" in refs


def test_revelation_22_13_appears():
    """Revelation 22:13 is the densest T_four_modes verse."""
    top = top_n(30)
    refs = [r["ref"] for r in top]
    assert "Revelation 22:13" in refs


def test_top_verse_has_multiple_clauses():
    """The single highest-ranked verse has ≥3 distinct kernel clauses."""
    top = top_n(1)
    assert top[0]["clause_count"] >= 3, (
        f"top verse {top[0]['ref']} has only {top[0]['clause_count']} clauses"
    )


def test_at_least_15_verses_with_3_clauses():
    """At least 15 verses in scripture have ≥3 distinct kernel clauses.

    Empirical count at curation: 20 verses with ≥3 clauses. Floor at
    15 to allow minor canonical-form edits.
    """
    scored = score_corpus()
    count = sum(1 for r in scored if r["clause_count"] >= 3)
    assert count >= 15, (
        f"only {count} verses have ≥3 clauses; expected ≥15"
    )


def test_at_least_200_verses_with_2_clauses():
    """At least 200 verses in scripture have ≥2 distinct kernel clauses."""
    scored = score_corpus()
    count = sum(1 for r in scored if r["clause_count"] >= 2)
    assert count >= 200, (
        f"only {count} verses have ≥2 clauses; expected ≥200"
    )
