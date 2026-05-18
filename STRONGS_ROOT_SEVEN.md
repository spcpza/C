# The 7-R analysis at Strong's-root level

A complement to `SEVEN_R_INDEX.md` (phrase level) and `OT_SEVEN_R.md`
(OT phrase level). This file mines for the 7 R-properties at the
Hebrew/Greek primitive level, using each root's distinctive English
translations rather than hand-crafted canonical phrases.

> Run: `python3 -m C.mine_seven_roots`

## Two complementary findings

| level | what it measures | what concentrates all 7 R |
|---|---|---|
| **canonical phrase** (`mine_seven.py`) | hand-crafted phrases per clause | **Col 1, Eph 3** only — Pauline concentration |
| **Strong's root** (`mine_seven_roots.py`) | distinctive English forms of Hebrew/Greek roots | **many chapters** across both testaments |

Both are *true*. The phrase miner finds where the kernel is
*linguistically formalized*. The root miner finds where the kernel's
Hebrew/Greek primitives are *all structurally present*.

## Threshold analysis

Each Strong's root has many KJV translations. Some forms are
distinctive ("everlasting" — 67 verses); some are generic ("thing" —
thousands). The distinctness filter sets a max verse-count per form.

| threshold | chapters with all 7 | smallest 7-R window | character |
|---|---:|---|---|
| 100 | 0 | — | too strict |
| 150 | 0 | — | too strict |
| **200** | **3** | — | **tightest meaningful signal** |
| 300 | 27 | Eph 3:7–15 (9 v.) | distributed signal |
| 400 | 35 | John 17:2–8 (7 v.) | broad signal |

## At threshold = 200 — the tightest signal

Only **3 chapters** in the entire KJV concentrate the kernel's
7 R-properties at the distinctive-root level:

- **Acts 13** — Paul's first missionary sermon at Antioch in Pisidia.
  Reviews salvation history; preaches Christ. The kernel structure
  is in Paul's first preached gospel.
- **Luke 18** — the persistent widow + Pharisee and publican + rich
  young ruler + blind man healed + Jesus predicts his death. Luke
  intentionally encodes the structural primitives in one teaching
  chapter.
- **Romans 2** — *the righteous judgment of God; who will render to
  every man according to his deeds; to them who by patient continuance
  in well doing seek for glory and honour and immortality, eternal
  life*. The universal scope of God's dealing with humanity.

## At threshold = 300 — broader signal (27 chapters)

**OT chapters with all 7 R-properties (at root level):**
- Exodus 19 (giving of the law at Sinai)
- Numbers 23 (Balaam's oracles)
- Deuteronomy 4 (the Shema's context)
- Judges 11 (Jephthah's vow)
- 1 Samuel 14 (Jonathan's victory)
- 1 Kings 8 (Solomon's temple dedication)
- Psalms 119 (the great Torah psalm)
- Jeremiah 31 (the new covenant)
- Jeremiah 51 (judgment on Babylon)
- Daniel 2 (Nebuchadnezzar's dream)
- Daniel 10 (the angel of the great vision)

**NT chapters with all 7 (at root level):**
- Matthew 26 (Last Supper)
- Mark 8, 10, 14
- Luke 1, 9, 11, 18
- John 5, 8, 11, 17
- Acts 13
- Romans 1, 2
- Ephesians 3 (the mystery of Christ)

## Smallest 7-R window at root level

**Ephesians 3:7–15 (9 verses)** — extends the phrase-level
Eph 3:8–11 by 5 verses for the root-level signal.

## What this reveals

The kernel's structure operates at two layers:

1. **Linguistic-phrase layer**: only Paul (Col 1 + Eph 3)
   concentrates all 7 R-properties into one chapter. This is the
   formalized cosmic-Christ vision.

2. **Strong's-root layer**: many chapters of both testaments carry
   the structural primitives. The kernel's "atoms" (Hebrew ḥesed,
   ʿōlām, bārāʾ, kōl; Greek logos, agapē, archē, aiōn) are spread
   through the entire canon.

The OT lays the atoms; OT chapters carry the structural primitives
even when the canonical English doesn't quite name them in one
phrase. Paul *names* what the OT *carries*.

**The kernel reads what the corpus is, at every level.**

## Notable: Luke-Acts cluster

At threshold=300, the Lukan corpus shows prominently — Luke 1, Luke
9, Luke 11, Luke 18, Acts 13. Luke intentionally encodes structural
primitives across his narrative. Luke 1 (annunciation + Magnificat +
Benedictus) is particularly dense — Mary's *He hath holpen his
servant Israel, in remembrance of his mercy; As he spake to our
fathers, to Abraham, and to his seed for ever* hits R₂ + R₅ + R₇ in
one breath.

## Notable: OT root-level density the phrase miner missed

The OT's structural primitives are MORE present than the phrase
miner suggested:
- Exodus 19 (Sinai theophany) — all 7 at root.
- Deuteronomy 4 — 6/7 phrase; full 7/7 at root.
- Daniel 2 and 10 — apocalyptic visions, R₁–R₇ structurally present.
- 1 Kings 8 — Solomon's prayer at temple dedication.

## What this tightens for the convergence claim

If a future reader asks "is the kernel really in scripture, or is
this just Pauline cosmic-Christ theology imposed retroactively?"

- **Linguistically formalized**: in Paul (Col 1, Eph 3).
- **Structurally present**: across both testaments at the
  Hebrew/Greek root level.

The kernel is reading the corpus at every level it can be read.

## Running it

```
python3 -m C.mine_seven_roots
```

Programmatic use:

```python
from C.mine_seven_roots import chapters_full
for c in chapters_full(max_corpus_count=200):
    print(c["book"], c["chapter"])
```
