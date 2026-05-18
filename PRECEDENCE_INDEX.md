# Precedence Index

Scripture's testimony that C/Word/God precedes everything — mined
from the KJV (31,102 verses) and curated.

The kernel's math is downstream of scripture. This file makes the
upstream visible.

> *In the beginning was the Word, and the Word was with God, and the
> Word was God.* — John 1:1

> *All things were made by him; and without him was not any thing made
> that was made.* — John 1:3

## How this file was built

`mine_precedence.py` scans every KJV verse for ten categories of
precedence-related phrases. `precedence.py` curates the highest-quality
anchors per kernel clause (R₁–R₇, T_bridge, T_four_modes, C_is_love,
plus logos_preexistence).

The corpus shows:

| category               | unique verses found |
|------------------------|--------------------:|
| pre_creation           |  70 |
| eternal_duration       |  67 |
| self_existence         | 189 |
| sourcing_through_C     |   6 |
| inexhaustibility       |  78 |
| invisibility           | 104 |
| uniqueness             |  38 |
| alpha_omega            |  12 |
| C_is_love              |  19 |
| logos_preexistence     |   6 |
| **total category-unique** | **~589** |

589 verses in the KJV directly assert some form of the precedence
claim the kernel formalizes. The kernel is not novel content; it is
the *structure* of what scripture already says in 589 places.

## Curated bridges by kernel clause

`precedence.py` carries 76 curated anchors. Run `python3 -m C.precedence`
for the live verified report; the table below is the snapshot.

### R₁ — existence of C
- John 1:1 — *In the beginning was the Word...*
- Exodus 3:14 — *I AM THAT I AM*
- Revelation 1:8 — *I am Alpha and Omega... the Almighty*
- Isaiah 44:6 — *I am the first, and I am the last*
- Isaiah 48:12 — *I am the first, I also am the last*
- Revelation 1:17, 2:8, 21:6 — the first / Alpha / beginning

### R₂ — atemporality (dC/dt = 0)
- Hebrews 13:8 — *same yesterday, and to day, and for ever*
- Malachi 3:6 — *I am the LORD, I change not*
- Psalms 102:27 — *thou art the same*
- James 1:17 — *no variableness, neither shadow of turning*
- Habakkuk 1:12 — *from everlasting, O LORD my God*
- Psalms 90:2 — *from everlasting to everlasting, thou art God*
- Psalms 41:13, 103:17, 106:48 — *from everlasting to everlasting*
- Isaiah 45:17, Ephesians 3:21 — *world without end*

### R₃ — universality (∀x: E(x, 0) = C)
- Colossians 1:17 — *he is before all things, and by him all things consist*
- Acts 17:28 — *in him we live, and move, and have our being*
- Ephesians 4:6 — *above all, and through all, and in you all*
- Romans 11:36 — *of him, and through him, and to him, are all things*
- 1 Corinthians 8:6 — *one God, the Father, of whom are all things*

### R₄ — sourcing (T₂)
- John 1:3 — *all things were made by him*
- Genesis 1:1 — *In the beginning God created*
- John 12:24 — *except a corn of wheat fall into the ground and die...*
- Colossians 1:16 — *by him were all things created*
- Hebrews 2:10 — *for whom are all things, and by whom are all things*
- Hebrews 1:10 — *in the beginning hast laid the foundation of the earth*

### R₅ — inexhaustibility (T₄)
- 1 Corinthians 13:8 — *charity never faileth*
- 1 John 4:8 — *God is love*
- John 4:14 — *a well of water springing up into everlasting life*
- Psalms 23:1 — *the LORD is my shepherd; I shall not want*
- Lamentations 3:22 — *of the LORD's mercies that we are not consumed*
- Isaiah 40:28 — *the everlasting God... fainteth not, neither is weary*

### R₆ — invisibility (T₃)
- 1 Timothy 1:17 — *the King eternal, immortal, invisible, the only wise God*
- Romans 1:20 — *the invisible things of him... clearly seen*
- John 1:18 — *no man hath seen God at any time*
- 1 Timothy 6:16 — *whom no man hath seen, nor can see*
- Colossians 1:15 — *the image of the invisible God*

### R₇ — pre-input (Self := C + ∫input ⟹ C is what was before any input)
- John 1:1 — *In the beginning was the Word*
- Genesis 1:1 — *In the beginning God created*
- Proverbs 8:23 — *set up from everlasting, from the beginning, or ever the earth was*
- Proverbs 8:25 — *before the mountains were settled, before the hills was I brought forth*
- John 17:5 — *the glory which I had with thee before the world was*
- John 17:24 — *thou lovedst me before the foundation of the world*
- Ephesians 1:4 — *chosen us in him before the foundation of the world*
- 1 Peter 1:20 — *foreordained before the foundation of the world*
- 2 Timothy 1:9 — *given us in Christ Jesus before the world began*
- Titus 1:2 — *promised before the world began*
- Micah 5:2 — *whose goings forth have been from of old, from everlasting*
- 1 John 1:1 — *that which was from the beginning*

### T_bridge — uniqueness
- Deuteronomy 6:4 — *the LORD our God is one LORD*
- Isaiah 45:5 — *I am the LORD, and there is none else, there is no God beside me*
- Isaiah 44:6 — *beside me there is no God*
- 1 Corinthians 8:6 — *there is but one God*
- 1 Timothy 2:5 — *there is one God, and one mediator*
- 1 Samuel 2:2 — *there is none holy as the LORD: for there is none beside thee*

### T_four_modes — origin = destination = way = holder = C
- Revelation 22:13 — *I am Alpha and Omega, the beginning and the end, the first and the last*
- Revelation 1:8 — *Alpha and Omega... the Almighty*
- Revelation 21:6 — *It is done. I am Alpha and Omega, the beginning and the end*
- John 14:6 — *I am the way, the truth, and the life*
- John 14:26 — *the Comforter, which is the Holy Ghost*

### C = love
- 1 John 4:8 — *God is love*
- 1 John 4:16 — *God is love; and he that dwelleth in love dwelleth in God*
- John 3:16 — *For God so loved the world, that he gave his only begotten Son*
- Romans 5:8 — *God commendeth his love toward us*
- John 13:34 — *love one another; as I have loved you*

### Logos / Wisdom pre-existence
- John 1:1 — *In the beginning was the Word...*
- John 1:2 — *the same was in the beginning with God*
- John 1:3 — *all things were made by him*
- Proverbs 8:22 — *the LORD possessed me in the beginning of his way, before his works of old*
- Proverbs 8:30 — *then I was by him, as one brought up with him*
- Colossians 1:15 — *the firstborn of every creature*
- Revelation 19:13 — *his name is called The Word of God*

## What this index shows

The scripture is *saturated* with precedence claims. The kernel's
clauses are not invented; they are the formalization of a structure
the corpus has stated in hundreds of places across both Testaments.

- **Pre-creation** language: 70+ verses (Gen 1:1, John 1:1, Prov 8,
  the Hebrews 1:10 *laid the foundation*, the *before the world* /
  *before the foundation* refrain in Pauline and Petrine letters).
- **Eternal duration**: 67+ verses (*from everlasting to everlasting*,
  *for ever and ever*, *world without end*).
- **Self-existence**: 189+ verses (the great I AM declarations,
  Alpha/Omega, *first and last*).
- **Universal sourcing through C**: every Pauline letter touches it.
- **Inexhaustibility**: the *never faileth* / *fainteth not* /
  *endureth for ever* family.
- **Invisibility**: *invisible, the only wise God*, *whom no man hath
  seen*.
- **Uniqueness**: the Shema, *there is none beside me*.
- **Alpha/Omega + the way + the Comforter**: the four-mode
  identifications.
- **C = love**: 1 John 4:8 / 4:16, plus John 3:16 and the *so loved
  the world* family.

> If you stack these verses on top of each other, the kernel's
> structure is what you see.

## Running the verification

```
python3 -m C.precedence       # curated bridge, verifies all 76 anchors
python3 -m C.mine_precedence  # full miner, ~589 unique hits
```

If any anchor ever fails to resolve in `word/`, the bridge is broken
and the test suite will say so (`tests/test_precedence.py`).
