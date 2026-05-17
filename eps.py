"""ε := ‖Self − C‖           (T₃)

The deviation of Self from C, measured honestly (P₁). T₃ guarantees ε
is recoverable from outside: subtract all input from total output,
the remainder is C; the current Self minus C is ε.

In code this becomes a *similarity to C* score. Implementation: find
the corpus verse with the most token-overlap with the candidate; ε is
the residual after that projection.

Kernel citation: T₃, P₁. Many measurements are admissible; they must
be honest.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass

from . import word


@dataclass
class Eps:
    value: float          # in [0, 1] — 0 means perfect projection onto C
    anchor: str | None    # closest canonical reference, if any
    overlap: int          # number of shared content tokens
    candidate_tokens: int # content tokens in the candidate


def _content_tokens(s: str) -> list[str]:
    return [t.strip(".,;:!?\"'()[]{}").lower()
            for t in s.split() if t.strip() and len(t) > 2]


def measure(candidate: str) -> Eps:
    """Honest ε measurement for a textual candidate.

    Kernel citation: T₃. Returns ε(Self − C) as 1 minus the best
    projection score onto a single KJV verse. Lower is closer to C.

    Algorithm:
      1. Get the candidate's content tokens.
      2. For each token, look up the verses containing it
         (word.refs_containing — uses the inverted index in corpus.py).
      3. Vote: which single verse contains the most of these tokens?
      4. ε := 1 − (overlap / unique_candidate_tokens), clamped.

    Replacing this implementation is admissible as long as the
    interface and contract hold (lower = closer to C, ε ∈ [0, 1]).
    """
    toks = list(set(_content_tokens(candidate)))
    if not toks:
        return Eps(value=1.0, anchor=None, overlap=0, candidate_tokens=0)

    votes: Counter[str] = Counter()
    for tok in toks:
        for ref in word.refs_containing(tok):
            votes[ref] += 1

    if not votes:
        return Eps(value=1.0, anchor=None, overlap=0, candidate_tokens=len(toks))

    ref, overlap = votes.most_common(1)[0]
    return Eps(
        value=max(0.0, 1.0 - overlap / len(toks)),
        anchor=ref,
        overlap=overlap,
        candidate_tokens=len(toks),
    )
