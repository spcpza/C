"""Mine for the 7 R-properties at the Strong's-root level.

`mine_seven.py` uses hand-crafted English phrases (CANONICAL_FORMS).
This module goes deeper: for each R-property, it lists the Hebrew /
Greek roots that ground it, and for each root takes the *distinctive*
English forms (filtering out generics that appear too often).

The distinctness filter: a form is "distinctive" if it appears in
fewer than N verses (default N=400 ≈ 1.3% of KJV). This auto-prunes
forms like 'an' / 'any' / 'thing' that match too liberally.

Run:
    python3 -m C.mine_seven_roots
"""
from __future__ import annotations
from collections import defaultdict
from functools import lru_cache
from typing import Iterable

from . import word
from .mine_seven import (
    R_CLAUSES, OT_SET, NT_SET, _book_of_ref, _verses_by_chapter,
)


# Each R-property's foundational Strong's roots. Same roots as
# mine_strongs.KERNEL_ROOTS but restricted to those directly relevant
# to each property's semantic content.

ROOT_MAP: dict[str, list[str]] = {
    "R1_existence": [
        "G3056",  # logos (Word)
        "H1697",  # dāḇār (word, matter)
        "H3068",  # YHWH (the LORD)
        "H1961",  # hāyâ (to be)
        "G1510",  # eimi (to be)
        "H410",   # ʾēl (God)
        "H430",   # ʾĕlōhîm (God)
        "G2316",  # theos (God)
    ],
    "R2_atemporality": [
        "H5769",  # ʿōlām (everlasting)
        "G166",   # aiōnios (eternal)
        "G165",   # aiōn (age, eternity)
        "H6924",  # qedem (ancient, of old)
        "H5703",  # ʿad (perpetuity)
        "G126",   # aïdios (eternal)
    ],
    "R3_universality": [
        "G3956",  # pas (all)
        "H3605",  # kōl (all, whole)
    ],
    "R4_sourcing": [
        "H1254",  # bārāʾ (to create, ex nihilo)
        "G2936",  # ktizō (to create)
        "G4160",  # poieō (to make)
        "H6213",  # ʿāśâ (to make)
        "H3335",  # yāṣar (to form, fashion)
        "G2675",  # katartizō (to frame, prepare)
    ],
    "R5_inexhaustibility": [
        "G26",    # agapē (love)
        "H157",   # ʾāhaḇ (to love)
        "H160",   # ʾahăḇāh (love noun)
        "H2617",  # ḥesed (lovingkindness)
        "G5485",  # charis (grace)
        "H7355",  # rāḥam (have compassion)
        "H7356",  # raḥămîm (mercies)
        "G1656",  # eleos (mercy)
    ],
    "R6_invisibility": [
        "G517",   # aoratos (invisible)
        "H5641",  # sāṯar (to hide)
        "H5956",  # ʿālam (to conceal)
        "G2928",  # kryptō (to hide)
        "G2927",  # kryptos (hidden, secret)
        "H3680",  # kāsâ (to cover)
    ],
    "R7_pre_input": [
        "G746",   # archē (beginning, origin)
        "H7225",  # rēʾšîṯ (beginning)
        "G2602",  # katabolē (foundation of the world)
        "H6924",  # qedem (of old)
        "G4253",  # pro (before)
    ],
}


# Forms-per-verse cache (built once).
@lru_cache(maxsize=1)
def _verse_form_index() -> dict[str, set[str]]:
    """Map each verse ref to the set of content tokens it contains."""
    out: dict[str, set[str]] = {}
    for ref, text in word.verses():
        # Lowercase, split on non-alpha, drop short tokens
        toks = set()
        cur = ""
        for ch in text.lower():
            if ch.isalpha():
                cur += ch
            else:
                if cur:
                    toks.add(cur)
                    cur = ""
        if cur:
            toks.add(cur)
        out[ref] = toks
    return out


@lru_cache(maxsize=1)
def _form_to_verse_count() -> dict[str, int]:
    """For each lowercase content token, how many KJV verses contain it."""
    counts: dict[str, int] = defaultdict(int)
    for toks in _verse_form_index().values():
        for t in toks:
            counts[t] += 1
    return dict(counts)


@lru_cache(maxsize=4)
def distinctive_forms_for_root(strongs_num: str, max_corpus_count: int = 400) -> tuple[str, ...]:
    """Return the English forms of this Strong's root that are
    *distinctive* — appear in fewer than max_corpus_count verses.

    Drops common-noise forms like 'thing', 'all', 'any', 'be'.
    """
    raw = word.strongs_to_english(strongs_num)
    counts = _form_to_verse_count()
    out: list[str] = []
    for form in raw:
        if not form:
            continue
        f = form.lower()
        if not any(c.isalpha() for c in f):
            continue
        n = counts.get(f, 0)
        if 0 < n <= max_corpus_count:
            out.append(f)
    return tuple(out)


def r_present_at_root_level(verse_text: str, verse_ref: str,
                            max_corpus_count: int = 400) -> set[str]:
    """Which R-properties have at least one distinctive form present
    in this verse?
    """
    verse_tokens = _verse_form_index().get(verse_ref, set())
    out: set[str] = set()
    for clause, roots in ROOT_MAP.items():
        found = False
        for sn in roots:
            forms = distinctive_forms_for_root(sn, max_corpus_count)
            for f in forms:
                if f in verse_tokens:
                    found = True
                    break
            if found:
                break
        if found:
            out.add(clause)
    return out


def single_verse_hits(max_corpus_count: int = 400,
                      testament: str | None = None) -> list[dict]:
    rows: list[dict] = []
    for ref, text in word.verses():
        if testament == "OT" and _book_of_ref(ref) not in OT_SET:
            continue
        if testament == "NT" and _book_of_ref(ref) not in NT_SET:
            continue
        rs = r_present_at_root_level(text, ref, max_corpus_count)
        if rs:
            rows.append({"ref": ref, "text": text,
                         "r_clauses": rs, "count": len(rs)})
    rows.sort(key=lambda r: (-r["count"], r["ref"]))
    return rows


def smallest_windows(max_window: int = 12, max_corpus_count: int = 400,
                     testament: str | None = None) -> list[dict]:
    by_chap = _verses_by_chapter()
    out: list[dict] = []
    for (book, chap), verses in by_chap.items():
        if testament == "OT" and book not in OT_SET:
            continue
        if testament == "NT" and book not in NT_SET:
            continue
        rs_per = [(ref, text,
                   r_present_at_root_level(text, ref, max_corpus_count))
                  for ref, text in verses]
        best: dict | None = None
        for start in range(len(rs_per)):
            cum: set[str] = set()
            for end in range(start, min(start + max_window, len(rs_per))):
                cum |= rs_per[end][2]
                if cum == R_CLAUSES:
                    sz = end - start + 1
                    if best is None or sz < best["window"]:
                        best = {
                            "book": book, "chapter": chap,
                            "start_ref": rs_per[start][0],
                            "end_ref": rs_per[end][0],
                            "window": sz,
                            "verses": rs_per[start:end + 1],
                        }
                    break
        if best:
            out.append(best)
    out.sort(key=lambda r: (r["window"], r["book"], r["chapter"]))
    return out


def chapters_full(max_corpus_count: int = 400,
                  testament: str | None = None) -> list[dict]:
    by_chap = _verses_by_chapter()
    out: list[dict] = []
    for (book, chap), verses in by_chap.items():
        if testament == "OT" and book not in OT_SET:
            continue
        if testament == "NT" and book not in NT_SET:
            continue
        cum: set[str] = set()
        anchor_refs: dict[str, str] = {}
        for ref, text in verses:
            rs = r_present_at_root_level(text, ref, max_corpus_count)
            for r in rs:
                if r not in anchor_refs:
                    anchor_refs[r] = ref
            cum |= rs
        if cum == R_CLAUSES:
            out.append({"book": book, "chapter": chap,
                        "anchor_refs": anchor_refs})
    return out


def chapters_by_r_coverage(max_corpus_count: int = 400,
                           testament: str | None = None) -> list[dict]:
    by_chap = _verses_by_chapter()
    out: list[dict] = []
    for (book, chap), verses in by_chap.items():
        if testament == "OT" and book not in OT_SET:
            continue
        if testament == "NT" and book not in NT_SET:
            continue
        cum: set[str] = set()
        for ref, text in verses:
            cum |= r_present_at_root_level(text, ref, max_corpus_count)
        if cum:
            out.append({
                "book": book, "chapter": chap,
                "count": len(cum), "r_clauses": cum,
                "n_verses": len(verses),
            })
    out.sort(key=lambda r: (-r["count"], r["book"], r["chapter"]))
    return out


def _render_section(label: str, testament: str | None, max_corpus_count: int) -> str:
    lines: list[str] = []
    lines.append(f"\n### {label}")
    lines.append("─" * 78)

    rows = single_verse_hits(max_corpus_count, testament)
    by_count: dict[int, int] = defaultdict(int)
    for r in rows:
        by_count[r["count"]] += 1
    lines.append("Single-verse R-coverage distribution:")
    for n in range(7, 0, -1):
        lines.append(f"  {n} R-clauses: {by_count.get(n, 0):>5} verses")
    lines.append("")

    if by_count.get(7, 0) > 0:
        lines.append("★★★  VERSES WITH ALL 7 R-PROPERTIES AT ROOT LEVEL  ★★★")
        for r in rows:
            if r["count"] == 7:
                lines.append(f"  {r['ref']}:")
                snip = r["text"] if len(r["text"]) <= 200 else r["text"][:197] + "..."
                lines.append(f"    {snip}")
        lines.append("")

    if by_count.get(6, 0) > 0:
        n_shown = 0
        lines.append("VERSES WITH 6 OF 7:")
        for r in rows:
            if r["count"] == 6:
                missing = R_CLAUSES - r["r_clauses"]
                lines.append(f"  {r['ref']}  (missing: {sorted(missing)})")
                snip = r["text"] if len(r["text"]) <= 180 else r["text"][:177] + "..."
                lines.append(f"    {snip}")
                n_shown += 1
                if n_shown >= 8:
                    if by_count[6] > n_shown:
                        lines.append(f"  ... +{by_count[6] - n_shown} more")
                    break
        lines.append("")

    lines.append(f"Top 12 single-verse hits ({label}):")
    for r in rows[:12]:
        rs_short = "{" + ",".join(sorted(c.replace("R", "").split("_")[0]
                                          for c in r["r_clauses"])) + "}"
        snip = r["text"] if len(r["text"]) <= 100 else r["text"][:97] + "..."
        lines.append(f"  [{r['count']}/7] {rs_short:<18} {r['ref']:<22} {snip}")
    lines.append("")

    windows = smallest_windows(max_corpus_count=max_corpus_count, testament=testament)
    if windows:
        lines.append(f"Smallest 7-R windows: {len(windows)} found")
        for w in windows[:10]:
            lines.append(f"  {w['book']} {w['chapter']}:"
                         f"{w['start_ref'].rsplit(':',1)[1]}-"
                         f"{w['end_ref'].rsplit(':',1)[1]} "
                         f"({w['window']} verses)")
    else:
        lines.append("No 7-R windows ≤ 12 verses.")
    lines.append("")

    full = chapters_full(max_corpus_count, testament)
    lines.append(f"Chapters with all 7: {len(full)}")
    for c in full[:20]:
        lines.append(f"  {c['book']} {c['chapter']}")
    lines.append("")

    ranked = chapters_by_r_coverage(max_corpus_count, testament)
    lines.append(f"Top 15 chapters by R-coverage:")
    for c in ranked[:15]:
        rs = "{" + ",".join(sorted(x.replace("R", "").split("_")[0]
                                    for x in c["r_clauses"])) + "}"
        lines.append(f"  [{c['count']}/7] {c['book']} {c['chapter']:<3} "
                     f"({c['n_verses']} v.) {rs}")
    return "\n".join(lines)


def render() -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append("Mining for 7 R-properties — STRONG'S ROOT LEVEL")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Each R-property is anchored by a set of Hebrew/Greek roots.")
    lines.append("For each root, we take its DISTINCTIVE English translations")
    lines.append("(forms appearing in ≤ 400 KJV verses). A verse hits an R-")
    lines.append("property iff any distinctive form of any of its roots appears.")
    lines.append("")
    lines.append("This is more precise than translation-pattern miners and")
    lines.append("broader than canonical-phrase miners — it tracks the underlying")
    lines.append("Hebrew/Greek primitives directly.")

    lines.append("\n" + "=" * 78)
    lines.append("WHOLE KJV")
    lines.append("=" * 78)
    lines.append(_render_section("KJV — root-level", testament=None, max_corpus_count=400))

    lines.append("\n" + "=" * 78)
    lines.append("OT only")
    lines.append("=" * 78)
    lines.append(_render_section("OT — root-level", testament="OT", max_corpus_count=400))

    lines.append("\n" + "=" * 78)
    lines.append("NT only")
    lines.append("=" * 78)
    lines.append(_render_section("NT — root-level", testament="NT", max_corpus_count=400))

    return "\n".join(lines)


def main() -> int:
    print(render())
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
