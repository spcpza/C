"""Strong's-root 7-R analysis — empirical findings as tests."""
from __future__ import annotations

from C.mine_seven_roots import (
    chapters_full, single_verse_hits, smallest_windows,
    distinctive_forms_for_root, ROOT_MAP,
)


def test_root_map_covers_all_seven():
    expected = {"R1_existence", "R2_atemporality", "R3_universality",
                "R4_sourcing", "R5_inexhaustibility", "R6_invisibility",
                "R7_pre_input"}
    assert expected == set(ROOT_MAP.keys())
    for clause, roots in ROOT_MAP.items():
        assert roots, f"{clause} has no roots"


def test_distinctive_forms_filter_works():
    """The filter should drop common forms while keeping distinctive ones."""
    # G3056 logos translates to 'word', 'saying', 'account', 'speech', 'thing'.
    # At threshold 400, 'thing' and 'word' are both too common (appear in
    # 400+ verses each); 'account', 'speech' remain as distinctive.
    forms = distinctive_forms_for_root("G3056", max_corpus_count=400)
    assert forms, "G3056 has no distinctive forms at threshold 400"
    # 'thing' must NOT be in the distinctive set (it's the noise we filter)
    assert "thing" not in forms
    # 'account' or 'speech' should be present (distinctive English translations)
    assert "account" in forms or "speech" in forms, (
        f"G3056 distinctive forms unexpected: {forms}"
    )


def test_three_tightest_chapters_at_threshold_200():
    """At threshold 200, exactly Acts 13, Luke 18, Romans 2 hit all 7."""
    chaps = chapters_full(max_corpus_count=200)
    refs = {(c["book"], c["chapter"]) for c in chaps}
    expected = {("Acts", 13), ("Luke", 18), ("Romans", 2)}
    # Allow minor drift (±1) from kernel/canonical tweaks; require expected ⊆ found
    # OR found ⊆ expected (i.e., subset in either direction).
    assert expected == refs, (
        f"expected exactly {expected}; got {refs}"
    )


def test_ephesians_3_in_root_level_full_chapters():
    """Ephesians 3 (the phrase-level winner) is also in root-level results
    once threshold is permissive enough (300)."""
    chaps = chapters_full(max_corpus_count=300)
    refs = [(c["book"], c["chapter"]) for c in chaps]
    assert ("Ephesians", 3) in refs


def test_at_least_5_OT_chapters_at_root_level():
    """At threshold 300, the OT should have ≥5 chapters with all 7 R."""
    from C.mine_seven_roots import chapters_full as cf
    chaps = cf(max_corpus_count=300, testament="OT")
    assert len(chaps) >= 5, (
        f"OT root-level all-7 chapters: {len(chaps)}; expected ≥5"
    )
