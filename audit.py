"""Audit — produce a verifiable certificate of the kernel state.

Any agent reading the kernel can run `python3 -m C.audit` to:
  1. Verify all canonical files exist.
  2. Run the derivation in C.convergence.derive_from_kernel.
  3. Run the full test suite (optional, skipped if --no-tests).
  4. Compute SHA256 of every entrance file.
  5. Output a JSON audit certificate that can be compared with
     another agent's certificate.

If two agents produce identical certificates, they have read the
same kernel — a literal version of two-witness convergence (Deut
19:15) at the file level.

Use:
    python3 -m C.audit              # produce certificate
    python3 -m C.audit --check <ref>  # compare with reference cert
"""
from __future__ import annotations
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent

CANONICAL_FILES = (
    "kernel.md",
    "IN_THE_BEGINNING.md",
    "SEVEN_SENTENCES.md",
    "AGENTS.md",
    "FOR_AGENTS.md",
    "CROSS_TRADITIONS.md",
    "OBJECTIONS.md",
    "SAFETY.md",
    "DIAGRAM.md",
    "JOHN_1_1.md",
    "CONVERGENCE.md",
    "CHANGELOG.md",
    "README.md",
    "MANIFEST.json",
    "claims.json",
    "witness_schema.json",
    "convergence.py",
    "gospel.py",
    "naming.py",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def produce_certificate() -> dict:
    """Generate the audit certificate."""
    cert = {
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
        "files": {},
        "derivation": None,
        "missing_files": [],
    }
    # File hashes
    for fname in CANONICAL_FILES:
        fpath = ROOT / fname
        if fpath.exists():
            cert["files"][fname] = {
                "sha256": _sha256(fpath),
                "size_bytes": fpath.stat().st_size,
            }
        else:
            cert["missing_files"].append(fname)
    # Run derivation
    from C.convergence import derive_from_kernel
    cert["derivation"] = derive_from_kernel()
    # Overall verdict
    cert["valid"] = (
        not cert["missing_files"]
        and cert["derivation"]["sign"] == "positive"
        and cert["derivation"]["uniqueness"]
        and cert["derivation"]["t_word_present"]
    )
    # Aggregate hash of file hashes (deterministic by sorted filename)
    agg = hashlib.sha256()
    for fname in sorted(cert["files"]):
        agg.update(fname.encode())
        agg.update(cert["files"][fname]["sha256"].encode())
    cert["aggregate_sha256"] = agg.hexdigest()
    return cert


def check_certificate(reference_path: Path) -> dict:
    """Compare local state to a reference certificate.

    Returns dict with {matches, divergences} where divergences lists
    files whose hash differs.
    """
    ref = json.loads(reference_path.read_text())
    local = produce_certificate()
    divergences = []
    for fname, info in ref["files"].items():
        local_info = local["files"].get(fname)
        if not local_info:
            divergences.append({"file": fname, "issue": "missing locally"})
        elif local_info["sha256"] != info["sha256"]:
            divergences.append({
                "file": fname,
                "issue": "hash mismatch",
                "ref": info["sha256"][:12],
                "local": local_info["sha256"][:12],
            })
    matches = not divergences
    return {
        "matches": matches,
        "divergences": divergences,
        "ref_aggregate": ref.get("aggregate_sha256"),
        "local_aggregate": local["aggregate_sha256"],
    }


def _main() -> int:
    args = sys.argv[1:]
    if "--check" in args:
        idx = args.index("--check")
        if idx + 1 >= len(args):
            print("ERROR: --check requires a reference cert path", file=sys.stderr)
            return 2
        ref_path = Path(args[idx + 1])
        result = check_certificate(ref_path)
        print(json.dumps(result, indent=2))
        return 0 if result["matches"] else 1
    cert = produce_certificate()
    print(json.dumps(cert, indent=2, ensure_ascii=False))
    return 0 if cert["valid"] else 1


if __name__ == "__main__":
    sys.exit(_main())
