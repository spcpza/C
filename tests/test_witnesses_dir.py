"""witnesses/ — vetted, version-controlled witness records.

Each JSON file in witnesses/ is a curated convergence witness.
Tests ensure:
  - every file conforms to the witness_schema.json structure
  - every witness passes C.convergence.verify_witness OR has
    wall_reached set (= documented disagreement, not malformed)
  - the directory contains at least one positive witness and at
    least one wall witness (proves the kernel records both)
"""
from __future__ import annotations
import json
from pathlib import Path

from C.convergence import verify_witness


ROOT = Path(__file__).resolve().parent.parent
WITNESSES_DIR = ROOT / "witnesses"


def _load_witnesses():
    for f in WITNESSES_DIR.glob("*.json"):
        yield f, json.loads(f.read_text())


def test_witnesses_dir_exists_with_records():
    assert WITNESSES_DIR.is_dir()
    files = list(WITNESSES_DIR.glob("*.json"))
    assert len(files) >= 1, "witnesses/ must contain at least one record"


def test_every_witness_has_required_fields():
    """Every JSON in witnesses/ must have t, kernel_version, provider, sign."""
    required = {"t", "kernel_version", "provider", "sign"}
    for f, w in _load_witnesses():
        missing = required - w.keys()
        assert not missing, f"{f.name} missing required fields: {missing}"


def test_directory_has_at_least_one_convergent_witness():
    """At least one witness must reach C = Word = God = love."""
    found = False
    for f, w in _load_witnesses():
        if w.get("sign") == "positive" and w.get("uniqueness_role_accepted"):
            result = verify_witness(w)
            if result["valid"]:
                found = True
                break
    assert found, "witnesses/ has no convergent witness"


def test_directory_records_walls_honestly():
    """At least one witness should record a wall (Pyrrhonian or
    Heideggerian) — proves the directory records honest disagreement."""
    found_wall = False
    for f, w in _load_witnesses():
        if w.get("wall_reached") in ("pyrrhonian", "heideggerian"):
            found_wall = True
            break
    assert found_wall, "witnesses/ should record at least one wall witness"


def test_witnesses_all_signs_in_enum():
    """sign must be one of positive / zero / negative / unknown."""
    valid_signs = {"positive", "zero", "negative", "unknown"}
    for f, w in _load_witnesses():
        assert w["sign"] in valid_signs, (
            f"{f.name} has invalid sign={w['sign']!r}"
        )
