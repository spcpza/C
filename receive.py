"""Mode-3 input gate. Orient toward sign_C; do not measure with high-ε self.

Kernel citation: §2.1 Theorem 2.4. An agent at ‖ε‖ > 0 cannot precisely
hold the rule it lives by. Modes 1 and 2 (memorize, look up) require
self-measurement and contradict. Mode 3 (Spirit holds, Self receives)
does not — receiving is orientation, not measurement.

In code this means: input is not first interpreted by the agent's own
prior beliefs. It is first *framed* against C, then handed to the
integrator. Interpretation comes later, after witnessing.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Any

from . import word


@dataclass
class Reception:
    """The result of receive() — input + an orientation toward C."""
    stimulus: Any                # the raw input
    anchors: list[tuple[str, str]]  # (ref, verse) pairs nearest in C
    uncertain: list[str]         # tokens with no anchor in C (P₃)
    strongs_roots: list[str]     # canonical roots resolved


def _tokens(s: str) -> list[str]:
    return [t.strip(".,;:!?\"'()[]{}").lower()
            for t in s.split() if t.strip()]


def receive(stimulus: Any, k: int = 3) -> Reception:
    """Receive a stimulus and orient toward C.

    Kernel citation: Theorem 2.4, P₃, T₃ (inverted-index anchor lookup).

    Concretely:
      1. Tokenize.
      2. For each token, mark whether it has a Strong's root and which
         KJV verses contain it (refs_containing).
      3. Score candidate verses by how many candidate tokens they
         contain; return the top-k as anchors.
      4. Tokens with no Strong's root *and* no KJV occurrence are
         marked Uncertain (P₃) but not dropped.

    For non-textual stimuli (e.g. ARC grids), the caller produces a
    textual description first; this is a deliberate bottleneck — the
    corpus is text, so the input must be framed in text to be
    oriented against it.
    """
    if not isinstance(stimulus, str):
        return Reception(
            stimulus=stimulus, anchors=[], uncertain=[repr(stimulus)[:80]],
            strongs_roots=[],
        )

    toks = [t for t in _tokens(stimulus) if len(t) > 2]
    uncertain: list[str] = []
    strongs_roots: list[str] = []
    ref_votes: Counter[str] = Counter()

    for tok in toks:
        roots = word.english_to_strongs(tok)
        if roots:
            strongs_roots.extend(roots)
        refs = word.refs_containing(tok)
        if not roots and not refs:
            uncertain.append(tok)
            continue
        # Each token votes for the verses it appears in.
        for ref in refs:
            ref_votes[ref] += 1

    top = ref_votes.most_common(k)
    anchors = [(ref, word.verse(ref)) for ref, _ in top]
    return Reception(
        stimulus=stimulus,
        anchors=anchors,
        uncertain=uncertain,
        strongs_roots=strongs_roots,
    )
