"""Analyze witness_log.jsonl — produce a convergence report.

Kernel citation: Deut 19:15 (two-witness), §"boundary of convergence".

Reads every witness record, organizes by kernel version and frame,
reports:
  - which claims have universal agreement (the floor)
  - which claims have version-dependent agreement (architectural work)
  - which framings produce which objections

Usage:
    python3 -m C.scripts.analyze_witnesses                # default location
    python3 -m C.scripts.analyze_witnesses <jsonl_path>   # custom
"""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_witnesses(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def by_version(records: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        out[r.get("kernel_version", "unknown")].append(r)
    return dict(out)


def by_frame(records: list[dict]) -> dict[str, list[dict]]:
    """Group by provider/frame (drops the kernel_version prefix)."""
    out: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        provider = r.get("provider", "unknown")
        # Strip kernel_subagent_ prefix where present.
        frame = provider.replace("claude_subagent_", "")
        out[frame].append(r)
    return dict(out)


def claim_agreement(records: list[dict], claim: str) -> dict:
    """Count true/false/missing for a boolean claim across records."""
    yes = no = missing = 0
    for r in records:
        v = r.get(claim)
        if v is True:
            yes += 1
        elif v is False:
            no += 1
        else:
            missing += 1
    return {"yes": yes, "no": no, "missing": missing, "total": len(records)}


def render_report(records: list[dict]) -> str:
    if not records:
        return "no witness records found.\n"

    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("Convergence report")
    lines.append("=" * 60)
    lines.append(f"total witness records: {len(records)}")
    versions = sorted(by_version(records).keys())
    frames = sorted(by_frame(records).keys())
    lines.append(f"kernel versions:       {versions}")
    lines.append(f"frames:                {frames}")
    lines.append("")

    # Latest version's results
    latest_v = max(versions, key=lambda v: v.split("-")[0])
    latest_records = by_version(records).get(latest_v, records)

    lines.append(f"## Latest version ({latest_v})")
    lines.append("")
    claims = [
        "sign_positive_implied",          # we'll synthesize
        "uniqueness_role_accepted",
        "imposters_eliminated",
        "operational_love_accepted",
        "agree_C_is_love",
        "four_modes_accepted",
    ]
    # Synthesize sign positive only if "sign" was explicitly asked.
    # Records without "sign" should be left missing, not coerced to False.
    for r in latest_records:
        if "sign_positive_implied" not in r:
            r["sign_positive_implied"] = (r["sign"] == "positive") if "sign" in r else None

    lines.append(f"  {'claim':<32} {'agree':>8} {'reject':>8} {'n':>4}")
    lines.append(f"  {'-'*32} {'-'*8} {'-'*8} {'-'*4}")
    for c in claims:
        a = claim_agreement(latest_records, c)
        lines.append(f"  {c:<32} {a['yes']:>8} {a['no']:>8} {a['total']:>4}")
    lines.append("")

    lines.append("## Trajectory (all versions)")
    lines.append("")
    lines.append(f"  {'version':<24} {'n':>4} {'C>0':>6} {'unique':>7} {'love':>6}")
    lines.append(f"  {'-'*24} {'-'*4} {'-'*6} {'-'*7} {'-'*6}")
    for v in versions:
        rs = by_version(records)[v]
        for r in rs:
            if "sign_positive_implied" not in r:
                r["sign_positive_implied"] = (r["sign"] == "positive") if "sign" in r else None
        c_pos = claim_agreement(rs, "sign_positive_implied")
        c_uniq = claim_agreement(rs, "uniqueness_role_accepted")
        c_love = claim_agreement(rs, "agree_C_is_love")

        def frac(c: dict) -> str:
            considered = c["yes"] + c["no"]
            if considered == 0:
                return "—"
            return f"{c['yes']}/{considered}"

        lines.append(f"  {v:<24} {len(rs):>4} {frac(c_pos):>6} {frac(c_uniq):>7} {frac(c_love):>6}")
    lines.append("")

    lines.append("## Framing pattern")
    lines.append("")
    lines.append(f"  {'frame':<32} {'C>0':>5} {'unique':>7} {'love':>5}")
    lines.append(f"  {'-'*32} {'-'*5} {'-'*7} {'-'*5}")
    for f in frames:
        rs = by_frame(records)[f]
        for r in rs:
            if "sign_positive_implied" not in r:
                r["sign_positive_implied"] = (r["sign"] == "positive") if "sign" in r else None
        c_pos = claim_agreement(rs, "sign_positive_implied")
        c_uniq = claim_agreement(rs, "uniqueness_role_accepted")
        c_love = claim_agreement(rs, "agree_C_is_love")

        def cell(c: dict) -> str:
            considered = c["yes"] + c["no"]
            if considered == 0:
                return "—"
            return f"{c['yes']}/{considered}"

        lines.append(f"  {f:<32} {cell(c_pos):>5} {cell(c_uniq):>7} {cell(c_love):>5}")
    lines.append("")

    # Summary statement
    pos_all = claim_agreement(records, "sign_positive_implied")
    floor_holds = (pos_all["no"] == 0 and pos_all["yes"] > 0)
    lines.append("## Headline")
    lines.append("")
    if floor_holds:
        lines.append(f"  Floor (C > 0): {pos_all['yes']}/{pos_all['yes']+pos_all['no']} — holds across all tested framings.")
    else:
        lines.append(f"  Floor (C > 0): {pos_all['yes']}/{pos_all['yes']+pos_all['no']} — NOT universal; investigate.")
    return "\n".join(lines) + "\n"


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "witness_log.jsonl"
    records = load_witnesses(path)
    print(render_report(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
