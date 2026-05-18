"""Analyze-witnesses smoke tests."""
from __future__ import annotations
from pathlib import Path

from C.scripts.analyze_witnesses import (
    load_witnesses, by_version, by_frame, claim_agreement, render_report,
)


def _log_path() -> Path:
    return Path(__file__).parent.parent / "witness_log.jsonl"


def test_log_loads():
    records = load_witnesses(_log_path())
    assert len(records) > 0, "witness_log.jsonl is empty; convergence record missing"


def test_floor_holds_in_record():
    """The convergence floor (sign = positive) should be unanimous in the record.

    Kernel citation: §"boundary of convergence". Even the hostile and
    Buddhist witnesses accept C > 0.

    Records without an explicit 'sign' field are skipped (some witness
    rounds asked different questions). Among records that DID answer
    'sign', all must say 'positive'.
    """
    records = load_witnesses(_log_path())
    signs = [r["sign"] for r in records if "sign" in r]
    assert signs, "no witness records contain an explicit 'sign' field"
    not_positive = [s for s in signs if s != "positive"]
    assert not not_positive, (
        f"convergence floor compromised: "
        f"{len(not_positive)}/{len(signs)} witnesses reject C > 0: {not_positive}"
    )


def test_render_report_runs():
    records = load_witnesses(_log_path())
    report = render_report(records)
    assert "Convergence report" in report
    assert "Headline" in report
    assert "Floor" in report
