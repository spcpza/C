"""audit.py — kernel state certificate.

Kernel citation: Deut 19:15. Two agents with identical certificates
have read the same kernel. Cryptographic two-witness.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

from C.audit import produce_certificate, CANONICAL_FILES


ROOT = Path(__file__).resolve().parent.parent


def test_certificate_is_valid():
    cert = produce_certificate()
    assert cert["valid"] is True, (
        f"certificate not valid; missing={cert.get('missing_files')}; "
        f"derivation={cert.get('derivation')}"
    )


def test_all_canonical_files_present():
    """No canonical file should be missing."""
    cert = produce_certificate()
    assert not cert["missing_files"], (
        f"missing files: {cert['missing_files']}"
    )


def test_certificate_is_deterministic():
    """Two consecutive certificates must produce the same aggregate
    SHA256 (assuming no edits in between)."""
    a = produce_certificate()
    b = produce_certificate()
    assert a["aggregate_sha256"] == b["aggregate_sha256"], (
        "audit certificate is non-deterministic — bug in hashing"
    )


def test_cli_audit_exits_zero():
    """`python3 -m C.audit` exits 0 when the kernel is intact."""
    result = subprocess.run(
        ["python3", "-m", "C.audit"],
        capture_output=True, text=True,
        cwd=str(ROOT.parent),
    )
    assert result.returncode == 0, (
        f"C.audit CLI returned {result.returncode}; "
        f"stderr: {result.stderr[:200]}"
    )
    cert = json.loads(result.stdout)
    assert cert["valid"] is True


def test_certificate_includes_derivation():
    """The certificate must embed C.convergence.derive_from_kernel()."""
    cert = produce_certificate()
    assert "derivation" in cert
    assert cert["derivation"]["sign"] == "positive"
    assert cert["derivation"]["t_word_present"] is True


def test_aggregate_sha256_is_hex():
    cert = produce_certificate()
    agg = cert["aggregate_sha256"]
    assert len(agg) == 64  # SHA256 hex
    int(agg, 16)  # must parse as hex
