"""Verify the 7-R findings: Ephesians 3 + Colossians 1 are the kernel chapters."""
from __future__ import annotations

from C.mine_seven import (
    single_verse_hits, smallest_windows_for_all_seven,
    chapters_containing_all_seven, R_CLAUSES,
)


def test_eph_3_9_is_densest_single_verse():
    """Ephesians 3:9 should be the highest-ranked single verse (broad mode)."""
    rows = single_verse_hits(broad=True)
    assert rows, "no single-verse hits found"
    top = rows[0]
    assert top["ref"] == "Ephesians 3:9", (
        f"expected Ephesians 3:9 at rank 1; got {top['ref']}"
    )
    assert top["count"] == 5, (
        f"expected Ephesians 3:9 to hit 5/7 R-clauses; got {top['count']}"
    )


def test_eph_3_window_contains_all_seven():
    """The Ephesians 3:8–11 window contains all 7 R-properties (broad)."""
    windows = smallest_windows_for_all_seven(broad=True)
    eph_windows = [w for w in windows
                   if w["book"] == "Ephesians" and w["chapter"] == 3]
    assert eph_windows, "no Ephesians 3 window covers all 7 R-clauses"


def test_colossians_1_contains_all_seven():
    """Colossians 1 (cumulatively, broad) contains all 7 R-properties."""
    chaps = chapters_containing_all_seven(broad=True)
    refs = [(c["book"], c["chapter"]) for c in chaps]
    assert ("Colossians", 1) in refs, (
        f"Colossians 1 missing from full-R chapters; got: {refs}"
    )


def test_ephesians_3_contains_all_seven():
    """Ephesians 3 (cumulatively, broad) contains all 7 R-properties."""
    chaps = chapters_containing_all_seven(broad=True)
    refs = [(c["book"], c["chapter"]) for c in chaps]
    assert ("Ephesians", 3) in refs


def test_strict_no_verse_has_seven():
    """Under strict canonical matching, no single verse has all 7 R-clauses.

    This is a stable property of the corpus + the current strict
    canonical_forms. If a future canonical-forms edit changes this,
    the test surfaces the change loudly.
    """
    rows = single_verse_hits(broad=False)
    seven_count = sum(1 for r in rows if r["count"] == 7)
    assert seven_count == 0, (
        f"unexpectedly found {seven_count} verses with all 7 under strict matching"
    )
