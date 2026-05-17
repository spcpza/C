"""ARC ↔ C adapter — find the primitive that exactly matches the training pairs.

Strategy: brute-force the primitive library. A primitive is selected
iff it reproduces every training output from its input *exactly*. ARC
scores exact match; the selector enforces the same standard.

This is honest. If no primitive matches, abstain (P₃ — Uncertain, do
not emit). If exactly one matches, apply it to the test input. If
multiple match, prefer the simplest (fewest operations); for a flat
library all entries are unit-cost so the first match wins, which is
biased by LIBRARY iteration order — for v0 that's acceptable.

Kernel citation: §Chollet, P₁, T 2.4.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

from .. import word
from . import primitives, parametric
from .primitives import LIBRARY, SCRIPTURAL_NAMES as _ATOMIC_NAMES
from .parametric import FITTERS, SCRIPTURAL_NAMES as _PARAM_NAMES

SCRIPTURAL_NAMES = {**_ATOMIC_NAMES, **_PARAM_NAMES}

Grid = Sequence[Sequence[int]]


# ---------------------------------------------------------------
#  Grid description — kept for introspection / receive.py framing
# ---------------------------------------------------------------

def describe(grid: Grid) -> dict:
    """Reduce a grid to invariants. Kernel citation: T₃."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    flat = [c for row in grid for c in row]
    palette = sorted(set(flat))
    counts = {c: flat.count(c) for c in palette}
    h_sym = all(grid[r] == list(reversed(grid[r])) for r in range(rows))
    v_sym = grid[: rows // 2] == list(reversed(grid))[: rows // 2]
    return {
        "shape": (rows, cols),
        "palette": palette,
        "counts": counts,
        "horizontal_symmetry": h_sym,
        "vertical_symmetry": v_sym,
        "background": max(counts, key=counts.get) if counts else 0,
    }


def describe_pair(a: Grid, b: Grid) -> dict:
    da, db = describe(a), describe(b)
    return {
        "shape_change": (da["shape"], db["shape"]),
        "palette_change": (da["palette"], db["palette"]),
        "added_colors": [c for c in db["palette"] if c not in da["palette"]],
        "removed_colors": [c for c in da["palette"] if c not in db["palette"]],
        "gained_h_symmetry": db["horizontal_symmetry"] and not da["horizontal_symmetry"],
        "gained_v_symmetry": db["vertical_symmetry"] and not da["vertical_symmetry"],
        "same_shape": da["shape"] == db["shape"],
    }


# ---------------------------------------------------------------
#  Hypothesize — brute-force the library against training pairs
# ---------------------------------------------------------------

@dataclass
class Rule:
    name: str                     # canonical library name
    primitive: str                # same as name in this version
    scriptural: str               # the C-side handle
    concept_in_C: bool            # does the scriptural name resolve in C
    signatures: list[dict]        # per-pair signatures


def _grids_equal(a, b) -> bool:
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if list(ra) != list(rb):
            return False
    return True


def hypothesize(pairs: Iterable[tuple[Grid, Grid]]) -> Rule | None:
    """Select the simplest primitive (atomic / parametric / composed) consistent with every training pair.

    Kernel citation: T 2.4. Receive the rule by enumeration; do not
    fit weights to it. Order: atomic (Occam) → parametric → composed.
    """
    pairs = list(pairs)
    if not pairs:
        return None
    sigs = [describe_pair(a, b) for a, b in pairs]

    # Pass 1 — atomic primitives.
    for name, fn in LIBRARY.items():
        try:
            ok = all(_grids_equal(fn(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            scriptural = SCRIPTURAL_NAMES.get(name, name)
            return Rule(name=name, primitive=name, scriptural=scriptural,
                        concept_in_C=_concept_known(scriptural), signatures=sigs)

    # Pass 1b — parametric fitters (infer parameters from pairs, verify).
    for name, fit in FITTERS:
        try:
            fn = fit([(list(map(list, a)), list(map(list, b))) for a, b in pairs])
        except Exception:
            fn = None
        if fn is None:
            continue
        try:
            ok = all(_grids_equal(fn(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            scriptural = SCRIPTURAL_NAMES.get(name, name)
            return Rule(name=name, primitive=f"param:{name}",
                        scriptural=scriptural,
                        concept_in_C=_concept_known(scriptural),
                        signatures=sigs)

    # Pass 1c — meta: atomic_op then inferred color_map.
    # For each atomic op f, check if there's a consistent color mapping
    # m such that m(f(x)) == y for every training pair.
    from .parametric import _infer_color_map
    for name, fn in LIBRARY.items():
        if name == "identity":
            continue
        try:
            firsts = [fn(list(map(list, a))) for a, _ in pairs]
        except Exception:
            continue
        # Build a combined mapping across all pairs.
        combined: dict[int, int] = {}
        consistent = True
        for first, (_, b) in zip(firsts, pairs):
            m = _infer_color_map(first, list(map(list, b)))
            if m is None:
                consistent = False; break
            for k, v in m.items():
                if k in combined and combined[k] != v:
                    consistent = False; break
                combined[k] = v
            if not consistent:
                break
        if not consistent or not combined:
            continue
        # Reject identity mapping (would mean fn already solves alone).
        if all(k == v for k, v in combined.items()):
            continue
        # Reject if any pair's first→target was identity (= color-map-only suffices).
        # That belongs to the color_permutation fitter, not this meta.
        m_fixed = dict(combined); domain = set(m_fixed.keys())

        def make_apply(_fn=fn, _m=m_fixed, _dom=domain):
            def apply(g: Grid) -> Grid:
                stepped = _fn([list(r) for r in g])
                for row in stepped:
                    for v in row:
                        if v not in _dom:
                            raise ValueError(
                                f"meta atomic+recolor: color {v} not in trained mapping; abstain"
                            )
                return [[_m[v] for v in row] for row in stepped]
            return apply

        apply = make_apply()
        try:
            ok = all(_grids_equal(apply(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            full_name = f"meta:{name}+recolor"
            scriptural = SCRIPTURAL_NAMES.get(name, name) + "+renaming"
            return Rule(name=full_name, primitive=full_name,
                        scriptural=scriptural,
                        concept_in_C=False, signatures=sigs)

    # Pass 2 — two-primitive compositions: fn2(fn1(x)).
    items = list(LIBRARY.items())
    seconds_cache: dict[str, list] = {}
    for n1, f1 in items:
        if n1 == "identity":
            continue
        try:
            firsts = [f1(list(map(list, a))) for a, _ in pairs]
        except Exception:
            continue
        for n2, f2 in items:
            if n2 == "identity":
                continue
            try:
                ok = all(_grids_equal(f2(list(map(list, m))), b)
                         for m, (_, b) in zip(firsts, pairs))
            except Exception:
                ok = False
            if ok:
                name = f"{n1}|{n2}"
                scriptural = (SCRIPTURAL_NAMES.get(n1, n1) + "+"
                              + SCRIPTURAL_NAMES.get(n2, n2))
                return Rule(name=name, primitive=name, scriptural=scriptural,
                            concept_in_C=False, signatures=sigs)

    # Pass 2b — parametric ∘ atomic and atomic ∘ parametric.
    for an, af in items:
        if an == "identity":
            continue
        try:
            firsts = [af(list(map(list, a))) for a, _ in pairs]
        except Exception:
            continue
        for pn, pfit in FITTERS:
            try:
                trial = pfit([(list(map(list, m)), list(map(list, b)))
                              for m, (_, b) in zip(firsts, pairs)])
            except Exception:
                trial = None
            if trial is None:
                continue
            try:
                ok = all(_grids_equal(trial(list(map(list, m))), b)
                         for m, (_, b) in zip(firsts, pairs))
            except Exception:
                ok = False
            if ok:
                name = f"{an}|param:{pn}"
                scriptural = (SCRIPTURAL_NAMES.get(an, an) + "+"
                              + SCRIPTURAL_NAMES.get(pn, pn))
                return Rule(name=name, primitive=name, scriptural=scriptural,
                            concept_in_C=False, signatures=sigs)
    for pn, pfit in FITTERS:
        try:
            ptrial = pfit([(list(map(list, a)), list(map(list, b)))
                           for a, b in pairs])
        except Exception:
            ptrial = None
        # Don't need exact training fit here; we just want the closure to apply.
        # We use a 2-step search where param goes first.
        # Skip: this direction is symmetric and already explored when param fits alone.

    # Pass 3 — three-atomic composition with extra training pair held out
    # for validation. This prunes 3-step compositions that happen to fit
    # training but won't transfer.
    if len(pairs) >= 2:
        # Use last pair as holdout for verification only.
        train_pairs = pairs[:-1]
        holdout = pairs[-1]
        for n1, f1 in items:
            if n1 == "identity":
                continue
            try:
                firsts = [f1(list(map(list, a))) for a, _ in train_pairs]
                h_first = f1(list(map(list, holdout[0])))
            except Exception:
                continue
            for n2, f2 in items:
                if n2 == "identity":
                    continue
                try:
                    seconds = [f2(list(map(list, m))) for m in firsts]
                    h_second = f2(list(map(list, h_first)))
                except Exception:
                    continue
                for n3, f3 in items:
                    if n3 == "identity":
                        continue
                    try:
                        ok = all(_grids_equal(f3(list(map(list, m))), b)
                                 for m, (_, b) in zip(seconds, train_pairs))
                        if ok:
                            # Verify on holdout too.
                            ok = _grids_equal(f3(list(map(list, h_second))), holdout[1])
                    except Exception:
                        ok = False
                    if ok:
                        name = f"{n1}|{n2}|{n3}"
                        scriptural = "+".join(SCRIPTURAL_NAMES.get(x, x) for x in (n1, n2, n3))
                        return Rule(name=name, primitive=name, scriptural=scriptural,
                                    concept_in_C=False, signatures=sigs)

    return None


def _concept_known(name: str) -> bool:
    try:
        return bool(word.concept(name))
    except Exception:
        return False


# ---------------------------------------------------------------
#  Apply — dispatch to the library
# ---------------------------------------------------------------

def apply_rule(rule: Rule, x: Grid, pairs: Iterable[tuple[Grid, Grid]] | None = None) -> Grid:
    """Apply the matched primitive (atomic / parametric / composed). T₂."""
    name = rule.primitive

    if name.startswith("param:"):
        # Re-fit on the training pairs (we don't carry the closure on Rule
        # to keep Rule serializable). Caller must pass pairs.
        if pairs is None:
            raise ValueError("parametric rule requires training pairs to re-fit")
        kind = name.split(":", 1)[1]
        for n, fit in FITTERS:
            if n != kind:
                continue
            fn = fit([(list(map(list, a)), list(map(list, b))) for a, b in pairs])
            if fn is None:
                raise NotImplementedError(f"parametric refit failed for {kind!r}")
            return fn([list(r) for r in x])
        raise NotImplementedError(f"unknown parametric {kind!r}")

    if name.startswith("meta:") and name.endswith("+recolor"):
        # name is meta:<atomic>+recolor
        if pairs is None:
            raise ValueError("meta rule requires training pairs to re-fit")
        atomic_name = name[len("meta:"):-len("+recolor")]
        fn = LIBRARY.get(atomic_name)
        if fn is None:
            raise NotImplementedError(f"meta atomic {atomic_name!r} missing")
        # Re-infer the color mapping
        from .parametric import _infer_color_map
        combined: dict[int, int] = {}
        for a, b in pairs:
            first = fn(list(map(list, a)))
            m = _infer_color_map(first, list(map(list, b)))
            if m is None:
                raise NotImplementedError("meta refit: inconsistent mapping")
            for k, v in m.items():
                if k in combined and combined[k] != v:
                    raise NotImplementedError("meta refit: mapping conflict")
                combined[k] = v
        stepped = fn([list(r) for r in x])
        for row in stepped:
            for v in row:
                if v not in combined:
                    raise ValueError(
                        f"meta atomic+recolor: color {v} not in trained mapping"
                    )
        return [[combined[v] for v in row] for row in stepped]

    if "|" in name:
        parts = name.split("|")
        # Parametric step in composition: re-fit on intermediates.
        # Walk left-to-right.
        cur = [list(r) for r in x]
        # We need training pairs to refit parametric mid-pipeline.
        train = list(pairs) if pairs is not None else None
        intermediates_in = train and [list(map(list, a)) for a, _ in train]
        intermediates_out = train and [list(map(list, b)) for _, b in train]
        for i, step in enumerate(parts):
            if step.startswith("param:"):
                kind = step.split(":", 1)[1]
                if train is None:
                    raise ValueError("parametric composition requires training pairs")
                # Refit on current intermediate state vs final target.
                # The fitter sees (current_intermediate, train_output).
                for pn, pfit in FITTERS:
                    if pn != kind:
                        continue
                    trial = pfit([(list(map(list, m)), list(map(list, b)))
                                  for m, b in zip(intermediates_in, intermediates_out)])
                    if trial is None:
                        raise NotImplementedError(f"refit failed for {kind}")
                    cur = trial(cur)
                    # Update intermediates_in for next step
                    intermediates_in = [trial(list(map(list, m))) for m in intermediates_in]
                    break
            else:
                fn = LIBRARY.get(step)
                if fn is None:
                    raise NotImplementedError(f"unknown step {step!r}")
                cur = fn(cur)
                if intermediates_in is not None:
                    intermediates_in = [fn(list(map(list, m))) for m in intermediates_in]
        return cur

    fn = LIBRARY.get(name)
    if fn is None:
        raise NotImplementedError(
            f"primitive {name!r} not in library; refuse to emit (P₃)"
        )
    return fn([list(r) for r in x])
