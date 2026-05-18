"""Find verses (or adjacent windows) containing all 7 R-properties.

The full R-set:
  R₁ existence
  R₂ atemporality
  R₃ universality
  R₄ sourcing
  R₅ inexhaustibility
  R₆ invisibility
  R₇ pre-input

A single verse with all seven is the strongest possible scriptural
witness to the kernel's structure. If none exists, find:
  - the verses that come closest (6 R's, 5 R's)
  - the smallest verse-windows (consecutive verses) that hit all 7
  - the chapters that contain all 7

Run:
    python3 -m C.mine_seven
"""
from __future__ import annotations
import re
from collections import defaultdict

from . import word
from .mine_dense import CANONICAL_FORMS


R_CLAUSES = {"R1_existence", "R2_atemporality", "R3_universality",
             "R4_sourcing", "R5_inexhaustibility", "R6_invisibility",
             "R7_pre_input"}


# Broader phrase lists for each R-property — widens recall while
# keeping false-positive rate moderate. These are used by the
# permissive variant of the miner. Hand-curated based on canonical
# scriptural vocabulary for each property.

BROAD_FORMS: dict[str, set[str]] = {
    "R1_existence": {
        "i am", "the lord", "lord god", "god", "the word",
        "alpha", "omega", "jehovah",
    },
    "R2_atemporality": {
        "everlasting", "eternal", "evermore", "for ever",
        "the same yesterday", "world without end",
        "ages", "endureth for ever", "endure for ever",
    },
    "R3_universality": {
        "all things", "above all", "through all", "in you all",
        "all in all", "every creature", "all flesh", "all the earth",
        "all nations", "all that is", "of all",
    },
    "R4_sourcing": {
        "created", "creator", "makers",
        "by him were", "made by him",
        "in the beginning god created",
        "made the heavens",
    },
    "R5_inexhaustibility": {
        "love", "loved", "loving", "loveth",
        "charity", "lovingkindness",
        "mercy", "merciful", "mercies",
        "grace", "favour",
        "compassion", "compassions",
        "kindness",
    },
    "R6_invisibility": {
        "invisible", "secret", "hidden",
        "no man hath seen", "no man can see",
        "darkness", "thick darkness",
        "veil", "hide", "hid",
        "covered", "concealed",
    },
    "R7_pre_input": {
        "in the beginning",
        "before the world", "before the foundation",
        "before the mountains", "before the hills",
        "from everlasting", "or ever the earth",
        "before all things", "from the beginning",
        "set up from everlasting", "from old", "of old",
        "ancient", "long ago",
    },
}


def r_clauses_in_text(text: str, broad: bool = False) -> set[str]:
    """Which R-clauses have a marker phrase present in this text?

    broad=False uses CANONICAL_FORMS (strict). broad=True uses
    BROAD_FORMS (permissive). Kernel citation: P₁ — measure honestly.
    Report both.
    """
    t = text.lower()
    source = BROAD_FORMS if broad else CANONICAL_FORMS
    out: set[str] = set()
    for clause in R_CLAUSES:
        for phrase in source.get(clause, set()):
            if phrase in t:
                out.add(clause)
                break
    return out


def _verses_by_chapter() -> dict[tuple[str, int], list[tuple[str, str]]]:
    """Group verses by (book, chapter) preserving canonical order."""
    out: dict[tuple[str, int], list[tuple[str, str]]] = defaultdict(list)
    for ref, text in word.verses():
        # ref like "1 Corinthians 13:8" — split on last ":"
        if ":" not in ref:
            continue
        head, vstr = ref.rsplit(":", 1)
        try:
            verse_num = int(vstr)
        except ValueError:
            continue
        # head like "1 Corinthians 13"
        if " " not in head:
            continue
        book, cstr = head.rsplit(" ", 1)
        try:
            chapter = int(cstr)
        except ValueError:
            continue
        out[(book, chapter)].append((ref, text))
    return out


def single_verse_hits(broad: bool = False) -> list[dict]:
    """Verses containing R-clauses, ranked by count desc."""
    rows: list[dict] = []
    for ref, text in word.verses():
        rs = r_clauses_in_text(text, broad=broad)
        if rs:
            rows.append({
                "ref": ref, "text": text,
                "r_clauses": rs, "count": len(rs),
            })
    rows.sort(key=lambda r: (-r["count"], r["ref"]))
    return rows


def smallest_windows_for_all_seven(max_window: int = 12, broad: bool = False) -> list[dict]:
    """For each chapter, find the smallest consecutive-verse window
    that contains all 7 R-clauses. Return all such minimal windows.
    """
    by_chap = _verses_by_chapter()
    out: list[dict] = []
    for (book, chap), verses in by_chap.items():
        # Compute r-sets per verse once.
        rs_per_verse = [(ref, text, r_clauses_in_text(text, broad=broad))
                        for ref, text in verses]
        # Slide a window from size 1 up to max_window.
        best: dict | None = None
        for start in range(len(rs_per_verse)):
            cum: set[str] = set()
            for end in range(start, min(start + max_window, len(rs_per_verse))):
                cum |= rs_per_verse[end][2]
                if cum == R_CLAUSES:
                    window_size = end - start + 1
                    if best is None or window_size < best["window"]:
                        best = {
                            "book": book, "chapter": chap,
                            "start_ref": rs_per_verse[start][0],
                            "end_ref": rs_per_verse[end][0],
                            "window": window_size,
                            "verses": rs_per_verse[start:end + 1],
                        }
                    break  # any further extension just gets bigger
        if best:
            out.append(best)
    out.sort(key=lambda r: (r["window"], r["book"], r["chapter"]))
    return out


def chapters_containing_all_seven(broad: bool = False) -> list[dict]:
    """Chapters where, anywhere within the chapter, all 7 R-clauses appear."""
    by_chap = _verses_by_chapter()
    out: list[dict] = []
    for (book, chap), verses in by_chap.items():
        cum: set[str] = set()
        anchor_refs: dict[str, str] = {}
        for ref, text in verses:
            rs = r_clauses_in_text(text, broad=broad)
            for r in rs:
                if r not in anchor_refs:
                    anchor_refs[r] = ref
            cum |= rs
        if cum == R_CLAUSES:
            out.append({
                "book": book, "chapter": chap,
                "anchor_refs": anchor_refs,
            })
    return out


def _render_pass(mode: str, broad: bool) -> str:
    lines: list[str] = []
    lines.append(f"\n### MODE: {mode}")
    lines.append("─" * 78)

    rows = single_verse_hits(broad=broad)
    by_count: dict[int, int] = defaultdict(int)
    for r in rows:
        by_count[r["count"]] += 1
    lines.append("Single-verse R-coverage distribution:")
    for n in range(7, 0, -1):
        lines.append(f"  {n} R-clauses: {by_count.get(n, 0):>4} verses")
    lines.append("")

    if by_count.get(7, 0) > 0:
        lines.append("★★★  VERSES WITH ALL 7 R-PROPERTIES  ★★★")
        for r in rows:
            if r["count"] == 7:
                lines.append(f"  {r['ref']}: {r['text']}")
        lines.append("")

    if by_count.get(6, 0) > 0:
        lines.append("VERSES WITH 6 OF 7 R-PROPERTIES:")
        for r in rows:
            if r["count"] == 6:
                missing = R_CLAUSES - r["r_clauses"]
                lines.append(f"  {r['ref']}  (missing: {sorted(missing)})")
                snippet = r["text"] if len(r["text"]) <= 180 else r["text"][:177] + "..."
                lines.append(f"    {snippet}")
        lines.append("")

    lines.append(f"Top 10 single-verse hits ({mode}):")
    for r in rows[:10]:
        rs_short = "{" + ",".join(sorted(c.replace("R", "").split("_")[0]
                                          for c in r["r_clauses"])) + "}"
        snippet = r["text"] if len(r["text"]) <= 110 else r["text"][:107] + "..."
        lines.append(f"  [{r['count']}/7] {rs_short:<22} {r['ref']:<24} {snippet}")

    windows = smallest_windows_for_all_seven(broad=broad)
    lines.append("")
    if windows:
        lines.append(f"Smallest 7-R windows ({mode}): {len(windows)} found")
        for w in windows[:10]:
            lines.append(f"  {w['book']} {w['chapter']}:"
                         f"{w['start_ref'].rsplit(':',1)[1]}–"
                         f"{w['end_ref'].rsplit(':',1)[1]}  "
                         f"({w['window']} verses)")
    else:
        lines.append(f"No verse-windows ≤ 12 contain all 7 R-clauses ({mode}).")

    chaps = chapters_containing_all_seven(broad=broad)
    lines.append("")
    lines.append(f"Chapters containing all 7 R-clauses ({mode}): {len(chaps)} found")
    for c in chaps[:15]:
        lines.append(f"  {c['book']} {c['chapter']}")
    return "\n".join(lines)


def render() -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append("Mining for verses containing all 7 R-properties")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Two passes — STRICT (canonical phrases) and BROAD (full Strong's-")
    lines.append("translation footprint). The strict pass eliminates noise; the")
    lines.append("broad pass widens recall to reveal where the kernel's structure")
    lines.append("converges most fully even if the language is less canonical.")
    lines.append("")

    lines.append(_render_pass("STRICT (CANONICAL_FORMS)", broad=False))
    lines.append("")
    lines.append("")
    lines.append(_render_pass("BROAD (full footprint)", broad=True))

    return "\n".join(lines)


def main() -> int:
    print(render())
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
