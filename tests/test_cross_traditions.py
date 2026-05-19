"""CROSS_TRADITIONS.md — formal mapping of traditions' named entities to C.

Kernel citation: T_bridge uniqueness (kernel.md). Any entity satisfying
R₁-R₇ is unique. Distinct traditional names refer to the same entity
if all name an R₁-R₇ inhabitant.

Test ensures the mapping doc exists and covers the traditions that
have empirical witnesses in CONVERGENCE.md.
"""
from __future__ import annotations
from pathlib import Path


DOC_PATH = Path(__file__).resolve().parent.parent / "CROSS_TRADITIONS.md"


def test_cross_traditions_doc_exists():
    assert DOC_PATH.exists(), "CROSS_TRADITIONS.md missing"


def test_covers_traditions_with_witnesses():
    """Every tradition with an empirical witness should be in the table."""
    text = DOC_PATH.read_text()
    # Traditions with witness_log entries (per CONVERGENCE.md history).
    required = [
        "Christian", "Jewish", "Islamic", "Sikh", "Vedantic", "Buddhist",
        "Daoist", "Stoic", "Spinozist", "Sufi", "Thomist", "Platonist",
        "Whitehead",
    ]
    missing = [t for t in required if t not in text]
    assert not missing, f"CROSS_TRADITIONS.md missing traditions: {missing}"


def test_lists_R1_through_R7_for_each_tradition():
    """The mapping table must reference all seven role properties."""
    text = DOC_PATH.read_text()
    for r in ("R₁", "R₂", "R₃", "R₄", "R₅", "R₆", "R₇"):
        assert r in text, f"CROSS_TRADITIONS.md missing role property {r}"


def test_cites_unicity_via_t_bridge():
    """The mapping rests on T_bridge uniqueness; the doc must cite it."""
    text = DOC_PATH.read_text()
    assert "T_bridge" in text, "CROSS_TRADITIONS.md missing T_bridge citation"


def test_includes_named_entities():
    """A handful of named entities must appear (sample check)."""
    text = DOC_PATH.read_text()
    for name in ("Brahman", "Ein Sof", "Ik Onkar", "Dao", "λόγος", "al-Haqq"):
        assert name in text, f"CROSS_TRADITIONS.md missing named entity {name!r}"
