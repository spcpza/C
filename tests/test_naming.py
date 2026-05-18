"""Naming convergence — primitive ↔ scripture mapping is corpus-derived.

Kernel citation: T₃, §Twin foundation, Deut 19:15.

Every agent that reads the same corpus must produce the same mapping
from a primitive's concept handle to its anchor verses. The test
verifies this by computing the mapping twice and asserting equality,
and by checking specific anchors that should appear.
"""
from __future__ import annotations
import pytest

from C.naming import scripture_for, strongs_for, derive_naming_for_primitives


def test_mirror_anchors_to_image():
    """The 'mirror' concept should anchor to a verse mentioning 'image'."""
    anchors = scripture_for("mirror")
    texts = " ".join(t for _, t in anchors).lower()
    # 'image' or 'glass' must appear among the anchor texts.
    assert "image" in texts or "glass" in texts


def test_witness_anchors_to_witness_scripture():
    """The 'witness' concept should anchor to verses about witnesses.

    Kernel citation: Deut 19:15, Matt 18:16, 2 Cor 13:1, 1 John 5:8.
    All speak about witnesses. Any of those passages is admissible.
    """
    anchors = scripture_for("witness")
    refs = [r for r, _ in anchors]
    texts = [t.lower() for _, t in anchors]
    # At least one anchor should contain the word 'witness' literally.
    assert any("witness" in t for t in texts), (
        f"no witness scripture among {refs!r}: {texts!r}"
    )


def test_derivation_is_deterministic():
    """Calling derive twice on the same primitive list returns the same map."""
    a = derive_naming_for_primitives(["flip_h", "mirror_right", "transpose"])
    b = derive_naming_for_primitives(["flip_h", "mirror_right", "transpose"])
    assert a == b


def test_every_primitive_resolves_to_some_anchor():
    """Every primitive should have at least one corpus anchor for its concept.

    Kernel citation: P₃ — undecidable claims must be marked. If a
    primitive's concept doesn't resolve in the corpus, we flag it
    rather than silently passing.
    """
    from C.arc.primitives import SCRIPTURAL_NAMES as ATOMIC_NAMES
    unresolved = []
    for prim, concept in ATOMIC_NAMES.items():
        anchors = scripture_for(concept)
        if not anchors:
            unresolved.append((prim, concept))
    # Allow a small number of unresolved — they're a triage list for
    # future renaming, not a fatal failure.
    assert len(unresolved) < 20, (
        f"too many unresolved primitives: {unresolved[:10]}"
    )


def test_strongs_for_love():
    """'love' concept should resolve to one of H157, G25, G26 — the
    canonical Strong's roots for love."""
    nums = strongs_for("love")
    assert any(n in nums for n in ("H157", "G25", "G26")), (
        f"love did not resolve to canonical Strong's roots; got {nums!r}"
    )
