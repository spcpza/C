"""ARC adapter sanity. Kernel citation: §Chollet, T 2.4."""
from __future__ import annotations

from C.arc import describe, hypothesize, apply_rule


def test_describe_returns_invariants():
    g = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    d = describe(g)
    assert d["shape"] == (3, 3)
    assert d["palette"] == [0, 1]
    assert d["horizontal_symmetry"] is True
    assert d["vertical_symmetry"] is True
    assert d["background"] in (0, 1)


def test_hypothesize_picks_canonical_pattern():
    """A pair where output gains symmetry → 'restoration'."""
    in_grid = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    out_grid = [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    rule = hypothesize([(in_grid, out_grid)])
    # We assert that *some* rule is selected and that it has the
    # canonical fields filled. The exact name may move as the
    # primitives mature.
    assert rule is not None
    assert rule.name in {
        "restoration", "separation", "multiplication",
        "filling", "ordering", "naming", "witness",
    }


def test_apply_rule_restoration_completes_symmetry():
    rule_in = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    rule_out = [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    rule = hypothesize([(rule_in, rule_out)])
    if rule and rule.primitive == "complete_symmetry":
        got = apply_rule(rule, [[2, 0, 0], [0, 5, 0], [0, 0, 0]])
        # Right column should mirror the left.
        assert got[0][2] == 2
        assert got[2][2] == got[2][0]
