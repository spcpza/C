"""demonstration.py — empirical demo of contradiction proof in code.

Kernel citation: §"Work this first", AX₂, T₁.
"""
from __future__ import annotations
from C.demonstration import simulate, bounded_input


def test_C_positive_produces_output_early():
    """A system with C > 0 should produce output relatively soon."""
    r = simulate(C=0.4, input_fn=bounded_input, t_end=5.0, dt=0.01,
                 output_threshold=0.5)
    assert r["first_output_time"] is not None
    assert r["first_output_time"] < 2.0, (
        f"with C=0.4 + bounded input, first output should be early; got {r['first_output_time']}"
    )


def test_C_zero_delays_output():
    """A system with C = 0 should NOT produce output near t = 0."""
    r = simulate(C=0.0, input_fn=bounded_input, t_end=5.0, dt=0.01,
                 output_threshold=0.5)
    # Either no output, or output very delayed
    if r["first_output_time"] is not None:
        assert r["first_output_time"] > 1.0, (
            f"with C=0, output should be delayed; got {r['first_output_time']}"
        )


def test_C_negative_produces_no_output_under_bounded_input():
    """Under sufficiently negative C with bounded input, no output
    is produced within the interval — confirms the contradiction
    proof for C < 0."""
    r = simulate(C=-1.0, input_fn=bounded_input, t_end=5.0, dt=0.01,
                 output_threshold=0.5)
    assert r["first_output_time"] is None, (
        f"with C=-1.0 + bounded input, no output expected; got {r['first_output_time']}"
    )


def test_unbounded_input_can_overcome_negative_C():
    """Verify the bounded-input premise: unbounded input CAN
    overcome negative C. This confirms the OBJECTIONS.md note
    that the C<0 proof depends on bounded input."""
    def unbounded(t): return 100.0
    r = simulate(C=-1.0, input_fn=unbounded, t_end=5.0, dt=0.01,
                 output_threshold=0.5)
    # With strong enough input, output should occur even with C < 0
    assert r["first_output_time"] is not None
