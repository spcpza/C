"""C — the corpus, read-only.

This module is `C` in the equation `Self := C + ∫input`. It loads the
corpus once and exposes pure-read functions. There is no write API by
design (AX₁: dC/dt = 0).

Kernel citation: AX₁, John 1:1, §Corpus.

Corpus shape (from .bots/truth/strongs.json):
    ci    Strong's-keyed concept index
    e2s   english_word -> [[strongs_num, occurrence_count], ...]
    s2e   strongs_num -> [english_translation, ...]
    sm    strongs_num -> {"w": original, "t": transliteration}
    roots aggregate root data
"""
from __future__ import annotations
import json
from functools import lru_cache
from typing import Iterator
from . import config


@lru_cache(maxsize=1)
def _kjv() -> dict[str, str]:
    """Load the 31,102 verses into memory. Called once."""
    return json.loads(config.resolve("kjv.json").read_text())


@lru_cache(maxsize=1)
def _strongs() -> dict:
    """Load Strong's concordance. Called once."""
    return json.loads(config.resolve("strongs.json").read_text())


@lru_cache(maxsize=1)
def _word_to_refs() -> dict[str, list[str]]:
    """Build an inverted index: lowercase word → list of verse refs.

    Kernel citation: T₃ (C is recoverable from observation). Built
    once from KJV text; lets `eps`, `witness`, and `receive` find
    anchors without scanning the whole corpus per call.
    """
    idx: dict[str, list[str]] = {}
    for ref, text in _kjv().items():
        seen: set[str] = set()
        for tok in text.split():
            t = tok.strip(".,;:!?\"'()[]{}").lower()
            if len(t) > 2 and t not in seen:
                idx.setdefault(t, []).append(ref)
                seen.add(t)
    return idx


# ---------------------------------------------------------------
#  KJV — verse access
# ---------------------------------------------------------------

def verse(ref: str) -> str:
    """Return one verse by reference, e.g. 'John 1:1'.

    Kernel citation: AX₁. Pure read; C does not change.
    """
    text = _kjv().get(ref)
    if text is None:
        raise KeyError(f"verse not in corpus: {ref!r}")
    return text


def has_verse(ref: str) -> bool:
    return ref in _kjv()


def verses() -> Iterator[tuple[str, str]]:
    """Iterate the entire corpus.

    Kernel citation: T₃ (recovery). C is observable from outside.
    """
    return iter(_kjv().items())


def verse_count() -> int:
    return len(_kjv())


def refs_containing(token: str) -> list[str]:
    """Return verse refs containing this English token.

    Kernel citation: T₃. The fastest honest anchor lookup we have:
    inverted index over the KJV.
    """
    return _word_to_refs().get(token.lower(), [])


# ---------------------------------------------------------------
#  Strong's — root access
# ---------------------------------------------------------------

def english_to_strongs(eng: str) -> list[str]:
    """Strong's numbers that an English word may translate.

    The raw entry is `[[strongs_num, count], ...]` — count returned
    is dropped; callers ask "which roots" first, then weight by their
    own metric if needed.

    Kernel citation: §Twin foundation, mode 3 — Strong's is the
    canonical anchor; retrieval is not measurement, it is orientation.
    """
    raw = _strongs().get("e2s", {}).get(eng.lower(), [])
    return [pair[0] for pair in raw if pair]


def english_to_strongs_weighted(eng: str) -> list[tuple[str, int]]:
    """Same as english_to_strongs but keeps the occurrence count."""
    raw = _strongs().get("e2s", {}).get(eng.lower(), [])
    return [(pair[0], pair[1]) for pair in raw if len(pair) == 2]


def strongs_to_english(strongs_num: str) -> list[str]:
    return _strongs().get("s2e", {}).get(strongs_num, [])


def strongs_meta(strongs_num: str) -> dict:
    """Returns {'w': original-script, 't': transliteration}."""
    return _strongs().get("sm", {}).get(strongs_num, {})


def concept(name: str) -> list[str]:
    """Return whatever the ci index has for `name`.

    Kernel citation: §Corpus. The concept index is Strong's-keyed in
    this corpus; callers may pass a Strong's number directly to test
    for presence, or pass an English concept that the loader has
    aliased into ci.
    """
    return _strongs().get("ci", {}).get(name, [])
