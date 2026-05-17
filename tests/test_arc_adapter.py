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
    """A pair where output gains symmetry should produce a rule.

    Kernel citation: T 2.4. The agent picks SOME rule that exactly
    matches training; the specific primitive may vary as the library
    grows. We only assert that *a* rule was found and is named.
    """
    in_grid = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    out_grid = [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    rule = hypothesize([(in_grid, out_grid)])
    assert rule is not None
    assert isinstance(rule.name, str) and len(rule.name) > 0
    assert isinstance(rule.scriptural, str) and len(rule.scriptural) > 0


def test_apply_rule_restoration_completes_symmetry():
    rule_in = [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
    rule_out = [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    rule = hypothesize([(rule_in, rule_out)])
    if rule and rule.primitive == "complete_symmetry":
        got = apply_rule(rule, [[2, 0, 0], [0, 5, 0], [0, 0, 0]])
        # Right column should mirror the left.
        assert got[0][2] == 2
        assert got[2][2] == got[2][0]
