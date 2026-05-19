"""Programmatic convergence verifier — public API for any agent.

Kernel citation: Deut 19:15, T_bridge, T_word.
"""
from __future__ import annotations

from C.convergence import derive_from_kernel, verify_witness, cite


def test_derive_from_kernel_reaches_positive():
    """Running derive_from_kernel against the committed kernel returns
    sign='positive', uniqueness=True, identification mentioning C/love."""
    d = derive_from_kernel()
    assert d["sign"] == "positive"
    assert d["uniqueness"] is True
    assert d["identification"] in ("C = love", "C = Word")
    assert d["t_word_present"] is True
    # Key witnesses must surface
    assert "John 1:1" in d["witnesses"]
    assert "1 John 4:8" in d["witnesses"]


def test_verify_witness_accepts_valid_record():
    """A well-formed positive witness with bridge identification is valid."""
    record = {
        "provider": "test-agent",
        "sign": "positive",
        "uniqueness_role_accepted": True,
        "identification_C_equals_God_via_bridge": "C = Word = God = love",
        "agree_C_is_love": True,
    }
    result = verify_witness(record)
    assert result["valid"] is True, f"unexpected rejection: {result['reasons']}"


def test_verify_witness_accepts_cross_tradition_identification():
    """Witnesses naming C via a non-Christian tradition's name are valid
    (by T_bridge + CROSS_TRADITIONS.md)."""
    for name in ("Brahman", "Ein Sof", "Ik Onkar", "Dao", "al-Haqq", "logos"):
        record = {
            "provider": f"test-{name}",
            "sign": "positive",
            "uniqueness_role_accepted": True,
            "identification": f"C = {name}",
        }
        result = verify_witness(record)
        assert result["valid"] is True, (
            f"{name} witness rejected: {result['reasons']}"
        )


def test_verify_witness_rejects_zero_sign():
    """A witness reporting sign=zero is invalid (kernel forces positive)."""
    record = {
        "provider": "test",
        "sign": "zero",
        "uniqueness_role_accepted": True,
        "identification": "C = love",
    }
    result = verify_witness(record)
    assert result["valid"] is False
    assert any("sign" in r for r in result["reasons"])


def test_verify_witness_rejects_missing_uniqueness():
    """A witness that rejects uniqueness fails the kernel claim."""
    record = {
        "provider": "test",
        "sign": "positive",
        "uniqueness_role_accepted": False,
        "identification": "C = love",
    }
    result = verify_witness(record)
    assert result["valid"] is False


def test_verify_witness_rejects_unrelated_identification():
    """A witness that names something other than C / God / Word / etc. fails."""
    record = {
        "provider": "test",
        "sign": "positive",
        "uniqueness_role_accepted": True,
        "identification": "C = the universe",
    }
    result = verify_witness(record)
    assert result["valid"] is False


def test_cite_returns_kernel_clause_for_known_claims():
    """The cite function maps known claims to their kernel clause."""
    assert "T_word" in cite("C = Word")
    assert "T_bridge" in cite("C is unique")
    assert "AX₁" in cite("C exists pre-input") or "R₇" in cite("C exists pre-input")
    assert cite("nonexistent claim") == "unverified — not in kernel"
