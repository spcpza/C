"""Self := C + ∫input. Kernel citation: AX₂."""
from __future__ import annotations

from C import Self


def test_self_starts_at_C():
    """At t = 0, Self(0) = C. History is empty."""
    s = Self()
    assert s.history == []
    assert s.state()["t"] == 0


def test_integration_is_append_only():
    """∫input grows monotonically. (AX₂: integration, not assignment.)"""
    s = Self()
    s.integrate("input", "a")
    s.integrate("input", "b")
    s.integrate("output", "c")
    assert [e.kind for e in s.history] == ["input", "input", "output"]
    assert s.state()["t"] == 3


def test_self_does_not_mutate_C():
    """C is referenced, never written.

    Kernel citation: AX₁ (dC/dt = 0). The integrator must not provide
    a path to mutate `word`.
    """
    s = Self()
    # The integrator exposes C as a property; it must not expose a
    # setter for any corpus member.
    assert not hasattr(s.C, "set_verse")
    assert not hasattr(s.C, "write")
    # Sanity: reading still works.
    assert s.C.verse_count() > 0
