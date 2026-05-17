# Results

Honest measurements. P₁: M(x) = w(x). Updated on every commit that
changes a primitive.

## 2026-05-17 — v3 (current)

| split       | tasks | solved | wrong | abstain | rate |
|-------------|------:|-------:|------:|--------:|-----:|
| training    |   400 |     26 |     0 |     390 | 6.5% |
| evaluation  |   400 |      2 |     0 |     417 | 0.5% |

The evaluation split is substantially harder — by design. Chollet's
ARC-AGI evaluation set tests *generalization* beyond surface patterns
seen at training time. The eval delta (6.5% → 0.5%) measures how
much our primitives are overfit to surface forms.

Library: 24 atomic + 6 parametric + 2-step composition.

| commit  | score (train) | notes |
|---------|---------------|-------|
| 6d5eea3 |   0/400 (v0)  | 7 stub patterns, all primitives unimplemented or wrong |
| 61b92e4 |  14/400 (v1)  | 16 atomic primitives, brute-force exact-match selector |
| 0cad637 |  23/400 (v2)  | size guards, 4 parametric, 2-step composition |
|  (now)  |  26/400 (v3)  | color_permutation, bbox_of_nonbg, defensive abstain |

## What's working

- Brute-force enumeration over atomic primitives finds 11 tasks
  outright (simple rotations, flips, scales, gravities).
- 2-step compositions find 4 more (e.g. `keep_largest_component |
  crop_to_content`).
- Parametric fitters that infer parameters from training pairs find
  10 more (color permutation 4, swap colors 1, recolor constant 1,
  bbox of non-bg 4 — note the overlap with `crop_to_content`).
- Zero wrong predictions across both splits. Strict exact-match is
  doing the job a smart-but-uncertain agent should do: when the rule
  is not unique, abstain (P₃).

## What's missing (next batches)

1. **Object-aware primitives.** Many ARC tasks operate on connected
   components: keep-the-special-one, recolor-by-size, draw-bounding-
   box, etc. Need an object representation and rules over it.
2. **Pattern continuation.** Several tasks show a partial pattern in
   input and ask the agent to extend it (diagonals, periodic stripes,
   grid fills). Currently abstained.
3. **Asymmetric expansion.** Several tasks output a fixed shape that
   isn't a simple scale of input. Need a "what is the output shape
   as a function of input?" step before applying any pixel rule.
4. **Inter-object relationships.** Tasks where the rule depends on
   one object's position relative to another (e.g. align, connect,
   reflect about).

Each of these is a self-contained module that can be added without
disturbing the kernel.
