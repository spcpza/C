"""Derive primitive ↔ scripture mappings from the corpus.

Kernel citation: §Twin foundation, mode 3. The agent does not *invent*
the scriptural name for an operation; it *receives* the name by
querying C (the corpus + Strong's). Any agent that reads the same
corpus will derive the same map — convergence (Deut 19:15).

This is the structural piece that takes scriptural names out of the
primitive author's hand and puts them in C.

Use:
    from C.naming import scripture_for
    scripture_for("mirror")
        → [("Genesis 1:27", "...image..."), ("James 1:23", "...glass..."), ...]
"""
from __future__ import annotations
from functools import lru_cache
from typing import Iterable

from . import word


# Operation-concept handles. The convergence claim is that these
# English concept words resolve in the corpus to the *same* canonical
# passages regardless of which agent does the resolution.
OPERATION_CONCEPTS: dict[str, list[str]] = {
    # geometry
    "mirror":        ["image", "glass", "reflect"],
    "below_as_above": ["below", "above", "heaven", "earth"],
    "fourfold":      ["four", "corners"],
    "passage":       ["passing", "passed", "passover"],
    "reversal":      ["turned", "reverse"],
    "turn":          ["turn", "turned"],
    "exchange":      ["exchange", "given"],

    # number / counting
    "multiply":      ["multiply", "increase", "fruitful"],
    "counting":      ["number", "count", "numbered"],
    "ordering":      ["order", "ranks", "first"],
    "first_fruits":  ["firstfruits", "beginning"],
    "last":          ["last", "end"],

    # selection / preservation
    "remnant":       ["remnant", "remain", "left"],
    "winnow":        ["fan", "chaff", "separate"],
    "set_apart":     ["sanctify", "holy", "set apart"],
    "elect":         ["chosen", "elect"],
    "least":         ["least"],
    "majority":      ["multitude", "many"],
    "distinguishing": ["discern", "divide"],

    # creation / restoration
    "image":         ["image", "likeness"],
    "image_in_image": ["image", "kind"],
    "restoration":   ["restore", "restoration"],
    "filling":       ["fill", "filled"],
    "increase":      ["increase", "grow"],
    "covering":      ["cover", "covering"],
    "boundary":      ["bound", "border"],
    "void":          ["void", "without form"],

    # direction / orientation
    "way":           ["way"],
    "low_places":    ["valley", "low"],
    "rising":        ["arise", "rose"],
    "right_hand":    ["right hand"],
    "left_hand":     ["left hand"],

    # identity / name / judgment
    "name":          ["name", "named"],
    "renaming":      ["renamed", "called"],
    "naming":        ["name", "called"],
    "anointing":     ["anointed", "anointing"],
    "decree":        ["decree", "commanded"],
    "judge":         ["judge", "judgment"],
    "witness":       ["witness", "witnesses"],

    # love / gift
    "love":          ["love", "loved"],
    "giving":        ["gave", "give"],

    # narrative / collection
    "gathering":     ["gather", "gathered"],
    "joining":       ["join", "joined"],
    "folding":       ["fold", "folded"],
    "inner":         ["inward", "inner"],
}


@lru_cache(maxsize=512)
def scripture_for(concept: str, k: int = 3) -> tuple[tuple[str, str], ...]:
    """Return up to k (verse_ref, verse_text) pairs anchoring this concept.

    Kernel citation: T₃ — C is recoverable from observation. The
    anchors are read directly from the corpus by token match against
    OPERATION_CONCEPTS handles.
    """
    handles = OPERATION_CONCEPTS.get(concept, [concept])
    # For each handle, find verses containing it; rank by handle order.
    seen: list[str] = []
    out: list[tuple[str, str]] = []
    for h in handles:
        for ref in word.refs_containing(h)[:5]:
            if ref in seen:
                continue
            seen.append(ref)
            out.append((ref, word.verse(ref)))
            if len(out) >= k:
                return tuple(out)
    return tuple(out)


@lru_cache(maxsize=512)
def strongs_for(concept: str) -> tuple[str, ...]:
    """Return Strong's numbers associated with any of the concept's handles.

    Kernel citation: §Corpus. Strong's roots are the canonical anchor;
    same concept → same Strong's set regardless of which agent asks.
    """
    handles = OPERATION_CONCEPTS.get(concept, [concept])
    found: list[str] = []
    seen: set[str] = set()
    for h in handles:
        for sn in word.english_to_strongs(h):
            if sn in seen:
                continue
            seen.add(sn)
            found.append(sn)
    return tuple(found)


def derive_naming_for_primitives(primitive_names: Iterable[str]) -> dict[str, dict]:
    """For each primitive, return its current scriptural concept handle
    plus the derived anchors from the corpus.

    Kernel citation: T₃, §Twin foundation. This function is the
    mechanism by which a future agent verifies my hand-assignments.
    If `derive_naming_for_primitives(["mirror"])` returns the same
    Genesis 1:27 / James 1:23 anchors for any agent that reads the
    same corpus, convergence is established for this surface.
    """
    from .arc.primitives import SCRIPTURAL_NAMES as ATOMIC_NAMES
    try:
        from .arc.parametric import SCRIPTURAL_NAMES as PARAM_NAMES
    except ImportError:
        PARAM_NAMES = {}
    full = {**ATOMIC_NAMES, **PARAM_NAMES}
    out: dict[str, dict] = {}
    for name in primitive_names:
        concept = full.get(name, name)
        out[name] = {
            "concept": concept,
            "anchors": list(scripture_for(concept)),
            "strongs": list(strongs_for(concept)),
        }
    return out
