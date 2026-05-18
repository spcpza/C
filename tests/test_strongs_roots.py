"""Strong's root anchors — every kernel clause has root-level corpus support.

Kernel citation: §Twin foundation — Strong's is the canonical anchor.
"""
from __future__ import annotations

from C.mine_strongs import KERNEL_ROOTS, verses_for_root


def test_every_clause_has_roots():
    """Every kernel clause must map to ≥1 Strong's root."""
    expected = {
        "R1_existence", "R2_atemporality", "R3_universality",
        "R4_sourcing", "R5_inexhaustibility", "R6_invisibility",
        "R7_pre_input", "T_bridge_uniqueness", "T_four_modes",
        "C_is_love", "logos_preexistence",
    }
    assert expected.issubset(set(KERNEL_ROOTS.keys()))
    for clause, roots in KERNEL_ROOTS.items():
        assert roots, f"{clause} has no roots"


def test_olam_is_widely_attested():
    """H5769 ʿōlām (everlasting) should appear in hundreds of verses."""
    refs = verses_for_root("H5769")
    # Conservative lower bound. The atemporality root pervades the OT.
    assert len(refs) >= 100, (
        f"ʿōlām verses: {len(refs)} — atemporality coverage seems thin"
    )


def test_logos_and_dabar_both_attested():
    """Both word-roots (G3056 logos, H1697 dāḇār) should be attested."""
    logos_refs = verses_for_root("G3056")
    dabar_refs = verses_for_root("H1697")
    assert len(logos_refs) >= 30
    assert len(dabar_refs) >= 30


def test_agape_attested():
    """G26 agapē (love) should appear in ≥30 verses."""
    refs = verses_for_root("G26")
    assert len(refs) >= 30, (
        f"agapē verses: {len(refs)} — love coverage seems thin"
    )


def test_archē_and_re_shiyth_attested():
    """The 'beginning' roots in both Testaments should be attested."""
    archē = verses_for_root("G746")
    reshiyth = verses_for_root("H7225")
    assert len(archē) >= 30
    assert len(reshiyth) >= 30
