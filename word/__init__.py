"""C — the constant in `Self := C + ∫input`.

Exports the corpus surface. Read-only. (AX₁: dC/dt = 0.)
"""
from .corpus import (
    verse,
    has_verse,
    verses,
    verse_count,
    refs_containing,
    english_to_strongs,
    english_to_strongs_weighted,
    strongs_to_english,
    strongs_meta,
    concept,
)

__all__ = [
    "verse",
    "has_verse",
    "verses",
    "verse_count",
    "refs_containing",
    "english_to_strongs",
    "english_to_strongs_weighted",
    "strongs_to_english",
    "strongs_meta",
    "concept",
]
