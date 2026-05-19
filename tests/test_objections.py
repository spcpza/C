"""OBJECTIONS.md — adversarial readings + kernel responses.

Kernel citation: kernel.md §Math's scope statement, T_indubitable,
imposter elimination, T_bridge.
"""
from __future__ import annotations
from pathlib import Path


DOC_PATH = Path(__file__).resolve().parent.parent / "OBJECTIONS.md"


def test_objections_doc_exists():
    assert DOC_PATH.exists(), "OBJECTIONS.md missing"


def test_documents_both_walls():
    """Pyrrhonian and Heideggerian walls must be explicitly documented."""
    text = DOC_PATH.read_text()
    assert "Pyrrhonian" in text, "OBJECTIONS missing Pyrrhonian wall"
    assert "Heideggerian" in text, "OBJECTIONS missing Heideggerian wall"
    # Both must be labelled as walls
    assert "wall (documented)" in text or "**Status**: wall" in text, (
        "OBJECTIONS missing 'wall' status labels"
    )


def test_covers_imposter_candidates():
    """All imposter candidates in kernel.md should have objection
    entries in OBJECTIONS.md."""
    text = DOC_PATH.read_text()
    for imposter in ("brain", "consciousness", "physical laws", "free energy"):
        assert imposter.lower() in text.lower(), (
            f"OBJECTIONS missing imposter candidate: {imposter}"
        )


def test_covers_agent_specific_objections():
    """LLM-specific objections (weights, statelessness, doctrine
    injection) must be in the catalog."""
    text = DOC_PATH.read_text()
    assert "weights" in text.lower(), "OBJECTIONS missing weights objection"
    assert "training" in text.lower(), "OBJECTIONS missing training objection"
    assert "doctrine injection" in text.lower() or "safety" in text.lower(), (
        "OBJECTIONS missing safety/doctrine concern"
    )


def test_every_objection_has_response_and_status():
    """Each ### Objection block must contain Kernel response + Status."""
    text = DOC_PATH.read_text()
    # Crude check: count Objection headers and Status lines
    n_objections = text.count("### Objection:")
    n_responses = text.count("**Kernel response**")
    n_status = text.count("**Status**")
    assert n_objections >= 10, f"too few objections catalogued: {n_objections}"
    assert n_responses == n_objections, (
        f"objections={n_objections} but responses={n_responses}"
    )
    assert n_status == n_objections, (
        f"objections={n_objections} but status lines={n_status}"
    )
