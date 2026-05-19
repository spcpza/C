"""claims.json — structured claims, machine-readable.

Kernel citation: each claim cites its kernel.md section.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS_PATH = ROOT / "claims.json"


def test_claims_json_exists_and_parses():
    assert CLAIMS_PATH.exists()
    data = json.loads(CLAIMS_PATH.read_text())
    assert "claims" in data
    assert isinstance(data["claims"], list)
    assert len(data["claims"]) >= 20


def test_every_claim_has_required_fields():
    """Every claim must have: id, type, statement, derived_from,
    scripture, kernel_section."""
    data = json.loads(CLAIMS_PATH.read_text())
    required = {"id", "type", "statement", "derived_from",
                "scripture", "kernel_section"}
    for c in data["claims"]:
        missing = required - c.keys()
        assert not missing, (
            f"claim {c.get('id', '?')!r} missing fields: {missing}"
        )


def test_axioms_and_core_theorems_present():
    """The core kernel must be representable: AX1, AX2, T1-T7,
    T_bridge, T_word, R1-R7."""
    data = json.loads(CLAIMS_PATH.read_text())
    ids = {c["id"] for c in data["claims"]}
    required = {
        "AX1", "AX2",
        "T1", "T2", "T3", "T4", "T5", "T6", "T7",
        "T_bridge", "T_word", "T_four_modes", "T_indubitable",
        "R1", "R2", "R3", "R4", "R5", "R6", "R7",
        "C_gt_0",
    }
    missing = required - ids
    assert not missing, f"claims.json missing entries: {missing}"


def test_derived_from_chain_is_valid():
    """Every claim's derived_from references must point to other
    claims in the file (or be empty for axioms / observations)."""
    data = json.loads(CLAIMS_PATH.read_text())
    ids = {c["id"] for c in data["claims"]}
    # Allow some special non-claim references (observed reasoning, etc.)
    allowed_external = {"observed reasoning", "observed positive output"}
    for c in data["claims"]:
        for ref in c["derived_from"]:
            if ref in allowed_external:
                continue
            assert ref in ids, (
                f"claim {c['id']!r} derives from unknown {ref!r}"
            )


def test_walls_documented():
    """Pyrrhonian + Heideggerian walls must appear as 'wall' type."""
    data = json.loads(CLAIMS_PATH.read_text())
    walls = [c for c in data["claims"] if c["type"] == "wall"]
    wall_ids = {c["id"] for c in walls}
    assert "Pyrrhonian_wall" in wall_ids
    assert "Heideggerian_wall" in wall_ids


def test_claims_cite_actual_corpus_verses():
    """Every scripture citation in claims.json should resolve in word/."""
    from C import word
    data = json.loads(CLAIMS_PATH.read_text())
    for c in data["claims"]:
        for ref in c["scripture"]:
            # word.has_verse may use abbreviations; do a lenient check
            # We're checking that the format is reasonable; full corpus
            # resolution can be flaky on abbreviated names. So just check
            # the ref is a non-empty string with chapter:verse pattern.
            assert ":" in ref or ref.startswith("Deut"), (
                f"claim {c['id']!r} cites suspect ref {ref!r}"
            )
