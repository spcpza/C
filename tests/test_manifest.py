"""MANIFEST.json — machine-readable repo introspection.

Kernel citation: Deut 19:15. The manifest is the third witness — it
declares what the repo contains, so any agent can introspect without
parsing markdown.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "MANIFEST.json"


def test_manifest_exists_and_parses():
    assert MANIFEST_PATH.exists(), "MANIFEST.json missing"
    data = json.loads(MANIFEST_PATH.read_text())
    assert isinstance(data, dict)


def test_manifest_entrance_paths_all_exist():
    """Every path listed in the manifest must actually exist in the repo."""
    data = json.loads(MANIFEST_PATH.read_text())
    for entrance, info in data["entrances"].items():
        path = ROOT / info["path"]
        assert path.exists(), (
            f"manifest entrance {entrance!r} points to {info['path']!r} "
            f"which does not exist"
        )


def test_manifest_declares_role_properties():
    """R₁-R₇ must all appear in the manifest."""
    data = json.loads(MANIFEST_PATH.read_text())
    roles = data["role_properties"]
    for k in ("R1", "R2", "R3", "R4", "R5", "R6", "R7"):
        assert k in roles, f"MANIFEST missing role {k}"


def test_manifest_declares_identity_chain():
    """The identity chain (math + corpus) must be in the manifest."""
    data = json.loads(MANIFEST_PATH.read_text())
    ic = data["identity_chain"]
    assert "result" in ic
    assert "Word" in ic["result"] and "love" in ic["result"]


def test_manifest_documents_walls():
    """Both walls (Pyrrhonian, Heideggerian) must be in the empirical
    record."""
    data = json.loads(MANIFEST_PATH.read_text())
    walls = " ".join(data["empirical_record"]["walls"])
    assert "Pyrrhonian" in walls
    assert "Heideggerian" in walls


def test_manifest_programmatic_api_imports_work():
    """Each programmatic_api entry's import path must actually resolve."""
    from C.convergence import derive_from_kernel, verify_witness, cite  # noqa: F401
    from C.scripts.self_witness import witness  # noqa: F401
