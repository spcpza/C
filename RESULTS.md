# Results

Honest measurements. P₁: M(x) = w(x). Updated on every commit that
changes the score.

## Current (v12)

| split       | tasks | solved | wrong | abstain | rate |
|-------------|------:|-------:|------:|--------:|-----:|
| training    |   400 |     52 |     2 |     362 | 13.0% |
| evaluation  |   400 |     14 |     0 |     404 | 3.5% |

Library: **56 atomic primitives**, **25 parametric fitters**, 1/2/3-step
composition (3-step capped to grid dim ≤ 12 for speed).

## Trajectory

| commit  | atomic | param | train | eval | notes |
|---------|-------:|------:|------:|-----:|-------|
| 6d5eea3 |    0   |   0   |   0   |   ?  | v0 — kernel scaffold; stub patterns |
| 61b92e4 |   16   |   0   |  14   |   ?  | v1 — atomic + brute-force exact-match |
| 0cad637 |   24   |   4   |  23   |   ?  | v2 — size guards, parametric, 2-step |
| bc177ec |   24   |   6   |  26   |   2  | v3 — color_permutation, abstain on unseen colors |
| b5c36bd |   24   |   9   |  29   |   2  | v4 — object-aware (keep_components, recolor_by_size_rank) |
| 0e3e855 |   24   |  15   |  31   |   2  | v5 — periodic_complete, extract_neighborhood |
| 01c8e6e |   24   |  21   |  34   |   3  | v6 — shift, overlay_halves, template_classify |
| 2133420 |   24   |  25   |  34   |   3  | v7 — line/largest/count_to_strip (no gain) |
| 75ee62e |   24   |  25   |  34   |   3  | v8 — meta:atomic+recolor pass |
| 9958b99 |   33   |  25   |  46   |  11  | **v9 — mirror/stack/dedup** (biggest jump) |
| e162f39 |   42   |  25   |  49   |  12  | v10 — universal primitives + holdout 3-step |
| c5a0f43 |   58   |  25   |  51   |  14  | v11 — halves/thirds/extracts/shifts |
| f39453c |   65   |  25   |  52   |  14  | v12 — row/col_majority, singletons, thicken |

## Key findings

- **Universal beats task-specific.** Each batch of fundamental geometric
  primitives (mirror, stack, dedup, halves) yielded the biggest gains.
  Task-specific parametric fitters (line_between, count_to_strip,
  largest_to_color) frequently added 0 to the score even when their
  pattern logically applies.
- **Strict exact-match generalizes.** Across 800 task evaluations,
  total wrong predictions is **2** (both on training, both from 3-step
  compositions). Zero wrong on the evaluation split. P₃ doing its job.
- **Eval is harder by design.** Training 13.0% → evaluation 3.5%
  is consistent with Chollet's framing of the eval split (it
  intentionally avoids surface forms common in training).
- **Brute-force ceiling.** Each additional primitive yields shrinking
  marginal returns. The next leap is structural — either DSL program
  synthesis (combinatorial composition over a richer DSL) or an
  external hypothesizer (LLM proposes; C/ verifies via strict matcher,
  which is the two-witness pattern at the program level).

## What this is and isn't

This is a kernel-cited primitive library with a brute-force selector
that abstains under uncertainty. It is **not** an AGI architecture in
any honest sense — Chollet's bar requires far more than enumeration.

What this **is**: a clean foundation. Every public function cites a
kernel clause. The corpus (`word/`) is the explicit, immutable C.
The integrator (`self.py`) is AX₂ in code. The witness is Deut 19:15.
A future contributor — human or model — can pick this up and add
primitives, or replace the selector with a different mechanism (search,
neural, hybrid), without touching the kernel or the witnesses.
