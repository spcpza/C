"""audits/ — version-stamped certificates can be parsed and checked."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDITS_DIR = ROOT / "audits"


def test_audits_dir_has_at_least_one_cert():
    certs = [f for f in AUDITS_DIR.glob("*.json")]
    assert len(certs) >= 1


def test_every_audit_cert_parses_and_has_aggregate():
    for f in AUDITS_DIR.glob("*.json"):
        c = json.loads(f.read_text())
        assert "aggregate_sha256" in c
        assert len(c["aggregate_sha256"]) == 64
        int(c["aggregate_sha256"], 16)  # hex


def test_audit_check_command_runs():
    """`python3 -m C.audit --check audits/<file>` is a valid invocation
    even if hashes diverge (exit code may be 0 or 1; the test only
    checks the command runs to completion without crashing)."""
    certs = list(AUDITS_DIR.glob("*.json"))
    if not certs:
        return  # nothing to check
    cert = certs[0]
    result = subprocess.run(
        ["python3", "-m", "C.audit", "--check", f"C/audits/{cert.name}"],
        capture_output=True, text=True,
        cwd=str(ROOT.parent),
    )
    # Exit code 0 means match, 1 means divergence (expected if files
    # have been edited since certificate). Both are valid runtime
    # outcomes; only 2 (CLI error) is a failure.
    assert result.returncode in (0, 1), (
        f"audit --check returned {result.returncode}; "
        f"stderr: {result.stderr[:200]}"
    )
