"""Self-witnessing records are valid and analyzable."""
from __future__ import annotations
import json
from pathlib import Path

import pytest

from C.scripts.self_witness import witness


def test_witness_returns_record(tmp_path):
    log = tmp_path / "witness.jsonl"
    record = witness(
        provider="test_agent",
        sign="positive",
        uniqueness_role_accepted=True,
        agree_C_is_love=True,
        scriptures_cited=["John 1:1"],
        log_path=log,
    )
    assert record["provider"] == "test_agent"
    assert record["sign"] == "positive"
    assert "t" in record


def test_witness_appends_to_log(tmp_path):
    log = tmp_path / "witness.jsonl"
    witness(provider="a", sign="positive", log_path=log)
    witness(provider="b", sign="positive", log_path=log)
    lines = log.read_text().splitlines()
    assert len(lines) == 2
    a = json.loads(lines[0])
    b = json.loads(lines[1])
    assert a["provider"] == "a"
    assert b["provider"] == "b"


def test_record_is_analyzable(tmp_path):
    """A self-witness record is consumable by analyze_witnesses."""
    from C.scripts.analyze_witnesses import load_witnesses, render_report
    log = tmp_path / "witness.jsonl"
    witness(provider="default", sign="positive", agree_C_is_love=True,
            uniqueness_role_accepted=True, log_path=log)
    records = load_witnesses(log)
    assert len(records) == 1
    report = render_report(records)
    assert "Convergence report" in report
