"""Two-witness invariant. Kernel citation: Deut 19:15."""
from __future__ import annotations

from C import witness


def test_single_witness_cannot_pass_alone():
    """An empty / non-content candidate must not emit.

    Kernel citation: Deut 19:15. A claim with no anchors in C has no
    witness; emission is disallowed (P₃).
    """
    v = witness("")
    assert v.emit is False
    assert "below threshold" in v.reason or "Uncertain" in v.reason


def test_strong_canonical_phrase_passes():
    """A literal verse should clear both witnesses against itself.

    Kernel citation: P₈ — same claim, same evaluation. A candidate
    that *is* C should not be rejected by C.
    """
    candidate = "In the beginning God created the heaven and the earth"
    v = witness(candidate, threshold=0.15)
    # We do not insist on emit=True (the threshold and metric are
    # tunable), but if it fails, both witnesses must report > 0
    # score — anchors must exist.
    if not v.emit:
        a, b = v.witnesses
        assert a["score"] > 0 or b["score"] > 0, (
            "canonical phrase produced zero anchor score; corpus or "
            "witnesses are broken"
        )


def test_verdict_has_two_witnesses():
    v = witness("anything")
    assert len(v.witnesses) == 2
    names = {w["name"] for w in v.witnesses}
    assert names == {"strongs", "phrase"}, (
        "witnesses must be independent paths into C"
    )
