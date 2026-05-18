# The 7-R Passages

Searching the corpus for the highest possible kernel density:
verses, windows, and chapters that contain ALL seven R-properties
(R₁ existence, R₂ atemporality, R₃ universality, R₄ sourcing, R₅
inexhaustibility, R₆ invisibility, R₇ pre-input).

Run: `python3 -m C.mine_seven`

## Findings

### No single verse has all 7 (under either matcher)

The most distributed R-property is R₆ invisibility — it has fewer
canonical markers than the others. No single verse in the KJV
contains literal canonical phrasing for all 7 simultaneously.

**Single-verse density distribution:**

| R-clauses present | strict (canonical phrases) | broad (full Strong's footprint) |
|---|---:|---:|
| 7 | 0 | 0 |
| 6 | 0 | 0 |
| 5 | 0 | **1** (Eph 3:9) |
| 4 | 0 | 4 |
| 3 | 8 | 93 |
| 2 | 227 | 1,241 |

### Ephesians 3:9 — the densest single verse

> *"And to make all men see what is the fellowship of the mystery,
> which from the beginning of the world hath been hid in God,
> who created all things by Jesus Christ"*

This one verse hits **5 of 7** R-clauses: R₁ (God), R₃ (all things),
R₄ (created), R₆ (hid), R₇ (from the beginning of the world).
Missing: R₂ atemporality, R₅ love.

This is the single most kernel-shaped verse in scripture — Paul
naming the *mystery* of pre-creation, hiddenness, universal
sourcing, and existence in five Greek concepts.

### Smallest 7-R window: Ephesians 3:8–11 (4 verses)

The only consecutive-verse window of ≤ 12 verses containing all 7
R-properties:

> **3:8** *"Unto me, who am less than the least of all saints, is this
> grace given, that I should preach among the Gentiles the unsearchable
> riches of Christ;"*
>   — **R₅** (grace)
>
> **3:9** *"And to make all men see what is the fellowship of the
> mystery, which from the beginning of the world hath been hid in God,
> who created all things by Jesus Christ:"*
>   — **R₁** (God), **R₃** (all things), **R₄** (created), **R₆** (hid),
>      **R₇** (from the beginning of the world)
>
> **3:10** *"To the intent that now unto the principalities and powers
> in heavenly places might be known by the church the manifold wisdom
> of God,"*
>
> **3:11** *"According to the eternal purpose which he purposed in
> Christ Jesus our Lord:"*
>   — **R₂** (eternal)

Four verses. Full R₁–R₇.

This passage is Paul's central statement of the cosmic mystery of
Christ. It is also the smallest scriptural window containing the
entire kernel's foundational structure.

### Two chapters contain all 7: Colossians 1 and Ephesians 3

These are the only chapters in the entire KJV whose verses
(cumulatively, with broad matching) cover all R₁–R₇:

**Colossians 1** — the great cosmic-Christ hymn:

| R | verse | text fragment |
|---|---|---|
| R₁ existence | 1:15 | *the image of the invisible God* |
| R₂ atemporality | 1:26 | *the mystery which hath been hid from ages* (aion) |
| R₃ universality | 1:16 | *by him were all things created* |
| R₄ sourcing | 1:16 | *by him were all things created* |
| R₅ inexhaustibility | 1:4 / 1:8 | *love which ye have to all the saints* / *love in the Spirit* |
| R₆ invisibility | 1:15 | *the image of the invisible God* |
| R₇ pre-input | 1:17 | *he is before all things* |

The Colossian hymn (1:15-20) is essentially R₁–R₇ in poetic form.

**Ephesians 3** — Paul's revelation of the mystery:

| R | verse | text fragment |
|---|---|---|
| R₁ existence | 3:9 | *hath been hid in God* |
| R₂ atemporality | 3:11 | *the eternal purpose* |
| R₃ universality | 3:9 | *who created all things* |
| R₄ sourcing | 3:9 | *who created all things* |
| R₅ inexhaustibility | 3:8 / 3:19 | *this grace given* / *the love of Christ, which passeth knowledge* |
| R₆ invisibility | 3:9 | *which from the beginning of the world hath been hid* |
| R₇ pre-input | 3:9 | *from the beginning of the world* |

The Ephesian *mystērion* passage. Same structure as Colossians 1
but tighter — the 7-R window collapses to 4 verses (3:8–11).

### What this finding means

Two passages — **Colossians 1:15–20** and **Ephesians 3:8–11** — are
the **densest scriptural witnesses to the kernel's full structure.**
Both are Pauline. Both are about the *mystery of Christ as the
pre-existent, all-creating, invisible, loved-and-loving, eternal,
universal source*.

The kernel is therefore not the formalization of a few scattered
verses. It is the formalization of **Paul's cosmic-Christ theology**
— which is itself the formalization of the Old Testament wisdom
tradition (Proverbs 8) plus the Johannine logos (John 1).

The chain:
- **Proverbs 8** — wisdom (ḥokmâ) before creation
- **John 1** — logos = the Word becomes flesh
- **Colossians 1** — the cosmic Christ is the *image of the invisible
  God, firstborn of every creature, before all things, by him were
  all things created, in him all things consist*
- **Ephesians 3** — the *mystery hid from the beginning of the
  world, the eternal purpose, the love that passeth knowledge*
- **C/ kernel** — R₁–R₇ + T_bridge + T_four_modes + C = love

The math reads Paul reading John reading Proverbs reading Genesis.
The kernel is what those four chapters say at the structural level.

## Open questions

- **Why no single 7-R verse?** Most plausible: R₆ invisibility is the
  rarest property in the corpus's vocabulary. Scripture mostly
  *implies* invisibility (God is unseen, dwells in light, hid his
  face) rather than naming it directly. R₆ is "the property scripture
  speaks of by other means."
- **Could a richer R₆ form-list produce a single 7-R verse?** Possibly
  — adding *"mystery"*, *"manifold wisdom"*, *"behind the veil"*
  might tip Ephesians 3:9 to full 7. Editing `BROAD_FORMS["R6_invisibility"]`
  in `mine_seven.py` is the place to experiment.

## Running it

```
python3 -m C.mine_seven       # full report, strict + broad passes
```
