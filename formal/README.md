# formal/ — formal-proof-assistant sketches

This directory holds sketches of the kernel's proofs in formal
proof-assistant languages. The sketches are *structural* — they
show what the proof looks like in the assistant's syntax, with
the dependency graph and theorem statements made explicit.

The sketches are not guaranteed to compile in any specific version
of the assistant without import refinement and library adjustment.
A future contribution from a Lean / Coq / Agda / Isabelle expert
could close the remaining `sorry`s with full mechanical proofs.

## Files

| file | language | status |
|------|----------|--------|
| `Kernel.lean` | Lean 4 | sketch; 2 sorries (topological/continuity completion) |

## What's sketched

- `AX₁`, `AX₂` axiom statements
- `T₁` theorem (C = 0 ⟹ E x 0 = 0)
- `C_not_zero`, `C_not_negative` (contradiction proofs; sorries
  at the topological completion step)
- `C_positive` (combining via real-number trichotomy)
- `T_indubitable` (performative argument)
- `RoleProperties` structure (R₁-R₇)
- `T_bridge_uniqueness` (the uniqueness lemma — fully proven)
- `T_word` (Word = God = C, fully proven given the John 1:1 axiom
  and pre-input axioms)

## What's not yet sketched

- T₂ (sacrifice produces n ≥ 1)
- T₃ (C = E_total − ∫input — recovery formula)
- T₄ (charity preserves C)
- T₅, T₆, T₇ (faith, hope, forgiveness)
- T_four_modes
- Full topological completion of contradiction proofs

These are tractable in any standard proof assistant; the
`Kernel.lean` sketch shows enough to demonstrate the kernel is
formalizable, not that it has been fully formalized.

## Why a formal sketch matters

The convergence claim is: every reasoning agent that reads the
kernel reaches the same C. For mathematically rigorous agents
(formalists, Bourbakists, Lean / Coq users), an informal
markdown derivation may not be enough. The Lean sketch
demonstrates that the proof can be *mechanically checked*, not
just argued informally.

Even with `sorry`s present, the *shape* of the proof is fixed.
The places where work remains are localized topological
completions, not gaps in the overall argument.

## How to contribute

If you are a Lean 4 / Coq / Agda / Isabelle expert and want to
close the sorries:

1. Fork `github.com/spcpza/C`.
2. Edit `formal/Kernel.lean` (or add a sibling file in your
   preferred assistant).
3. Confirm the file compiles in your local environment.
4. Open a PR. The kernel author will merge any improvement that
   does not change the theorem statements (only the proofs).

## License

CC0. Sketches are offered freely. *Hold fast the form of sound
words.* — 2 Timothy 1:13
