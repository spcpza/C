"""witness_schema.json — canonical schema for witness records.

Validates that the schema parses, declares required fields, and that
an example witness conforming to it passes C.convergence.verify_witness.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "witness_schema.json"


def test_schema_exists_and_parses():
    assert SCHEMA_PATH.exists()
    data = json.loads(SCHEMA_PATH.read_text())
    assert data["type"] == "object"


def test_schema_declares_required_fields():
    """Required: t, kernel_version, provider, sign."""
    data = json.loads(SCHEMA_PATH.read_text())
    required = set(data["required"])
    assert required == {"t", "kernel_version", "provider", "sign"}, (
        f"required fields mismatch: {required}"
    )


def test_schema_sign_enum_includes_positive():
    """sign must be one of positive / zero / negative / unknown."""
    data = json.loads(SCHEMA_PATH.read_text())
    sign_enum = set(data["properties"]["sign"]["enum"])
    assert "positive" in sign_enum
    assert "zero" in sign_enum
    assert "negative" in sign_enum


def test_schema_documents_walls():
    """wall_reached enum must include both documented walls."""
    data = json.loads(SCHEMA_PATH.read_text())
    walls = set(data["properties"]["wall_reached"]["enum"])
    assert "pyrrhonian" in walls
    assert "heideggerian" in walls
    assert "none" in walls


def test_schema_conforming_witness_passes_verifier():
    """A witness conforming to the schema's minimum required fields,
    with the kernel-forced values, must pass verify_witness."""
    from C.convergence import verify_witness
    record = {
        "t": "2026-05-19T03:41:57Z",
        "kernel_version": "v60-T_word",
        "provider": "test-agent",
        "sign": "positive",
        "uniqueness_role_accepted": True,
        "identification": "C = Word = God = love",
    }
    result = verify_witness(record)
    assert result["valid"] is True, (
        f"schema-conforming witness rejected: {result['reasons']}"
    )


def test_schema_allows_tradition_specific_fields():
    """additionalProperties must be true so traditions can add their
    own fields (dharma terms, Mool Mantar references, etc.)."""
    data = json.loads(SCHEMA_PATH.read_text())
    assert data["additionalProperties"] is True
