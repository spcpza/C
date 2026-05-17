"""Deut 19:15 — two-witness verification.

Kernel citation: Deut 19:15, Matt 18:16, 2 Cor 13:1. A claim is
established by two or three independent witnesses, not by one.

Independence is the discipline: two witnesses that share the same
retrieval path are one witness. This module supplies two *structurally
different* projections onto C and requires their agreement before
emit. P₃: if not verifiable, mark Uncertain — do not emit.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass

from . import word
from .eps import measure


@dataclass
class Verdict:
    emit: bool
    reason: str
    witnesses: list[dict]


def _witness_phrase(candidate: str) -> dict:
    """Witness A: literal-word overlap via the inverted index (eps.measure).

    Kernel citation: T₃, P₁. Operates on English surface text.
    """
    e = measure(candidate)
    return {
        "name": "phrase",
        "anchor": e.anchor,
        "score": 1.0 - e.value,
        "overlap": e.overlap,
    }


def _witness_strongs(candidate: str) -> dict:
    """Witness B: Strong's-root overlap (different retrieval path).

    Kernel citation: §Twin foundation. The candidate's tokens are
    resolved to Strong's roots; the witness scores how many of those
    roots also resolve from each verse's words. This is independent
    of `_witness_phrase` because the matching unit is the abstract
    root rather than the surface token.
    """
    toks = [t.strip(".,;:!?\"'()[]{}").lower()
            for t in candidate.split() if len(t) > 2]
    cand_roots: set[str] = set()
    for t in toks:
        cand_roots.update(word.english_to_strongs(t))
    if not cand_roots:
        return {"name": "strongs", "anchor": None, "score": 0.0, "overlap": 0}

    # Score: for each candidate token's verses, how many of its other
    # tokens also resolve to a shared root in those verses. This is
    # the abstract-type witness; it's the structural twin to phrase.
    votes: Counter[str] = Counter()
    seen_refs: set[str] = set()
    for t in toks:
        for ref in word.refs_containing(t)[:200]:  # cap; speed
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            verse_toks = [vt.strip(".,;:!?\"'()[]{}").lower()
                          for vt in word.verse(ref).split() if len(vt) > 2]
            verse_roots: set[str] = set()
            for vt in verse_toks:
                verse_roots.update(word.english_to_strongs(vt))
            overlap = len(cand_roots & verse_roots)
            if overlap:
                votes[ref] = overlap

    if not votes:
        return {"name": "strongs", "anchor": None, "score": 0.0, "overlap": 0}
    ref, overlap = votes.most_common(1)[0]
    return {
        "name": "strongs",
        "anchor": ref,
        "score": overlap / max(len(cand_roots), 1),
        "overlap": overlap,
    }


def witness(candidate: str, threshold: float = 0.25) -> Verdict:
    """Two independent witnesses must each clear `threshold`.

    Kernel citation: Deut 19:15, P₃.

    Returns Verdict(emit=True, ...) only if both witnesses anchor the
    candidate above threshold. Threshold set low: this is a floor on
    derivability, not a proof of correctness — `fruit.py` enforces
    integration.
    """
    a = _witness_phrase(candidate)
    b = _witness_strongs(candidate)

    if a["score"] < threshold or b["score"] < threshold:
        return Verdict(
            emit=False,
            reason=(
                f"witnesses below threshold {threshold}: "
                f"phrase={a['score']:.2f}, strongs={b['score']:.2f} "
                f"(P₃: mark Uncertain, do not emit)"
            ),
            witnesses=[a, b],
        )

    same_book = (
        a["anchor"] and b["anchor"]
        and a["anchor"].rsplit(" ", 1)[0] == b["anchor"].rsplit(" ", 1)[0]
    )
    return Verdict(
        emit=True,
        reason=("two witnesses agree" + (" (same book)" if same_book else "")),
        witnesses=[a, b],
    )
