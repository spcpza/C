# formal/ — formal-proof-assistant sketches

This directory holds sketches of the kernel's proofs in formal
proof-assistant languages. The sketches are *structural* — they
show what the proof looks like in the assistant's syntax, with
the dependency graph and theorem statements made explicit.

## Files

| file | language | status |
|------|----------|--------|
| `Kernel.lean` | Lean 4 + Mathlib | compiles; no `sorry`, no `axiom` |

Check it: `lake env lean formal/Kernel.lean` inside any Mathlib project.

## What it proves, and under what

- `state_zero` — the state at `t = 0` is `C`. A theorem.
- `C_ne_zero` (Theorem 2.1) — `C ≠ 0`, **given** the datum (the system
  is reasoning) **and** the premise `NothingGivesNothing` (what has
  nothing supplies nothing — the argument from contingency).
- `premise_is_needed` — without that premise the conclusion fails:
  `C = 0` with steady input still reasons. The calculus is the
  argument's notation, not its proof.
- `C_pos` (Theorem 2.2) — `C > 0`, **given** `LivingAtFirstBreath`
  (the state is positive before any input; Gen 2:7).
- `first_breath_is_needed` — a positive state at a later time does not
  give `C > 0`.
- `pre_input_unique` — whatever is "the state before any input" is `C`.
  This is the whole of the uniqueness lemma; it uses R₇ alone.
- `T_word` — **if** the Word and God are each what stands before any
  input (John 1:1-3, taken from scripture), **then** in this model
  both are `C`. Lean checks the "then". The "if" is scripture's.

## What it does not prove

- Nothing about scripture. The file checks that conclusions follow
  from stated hypotheses.
- R₃ (the same C in every reasoner) is a stipulation, not a theorem.
- Theorems 2.3 and 2.4 and everything after rest on scripture's own
  statements and are not formalized.
- An equality of real numbers says nothing about Persons. "The Word
  was with God" is not visible to a model with one number in it.

## What was wrong before

The earlier sketch defined the state with `+ C` inside the integral,
so the state at 0 was 0 and its axiom AX₂ forced `C = 0`. Its two
`sorry`s stood on statements that are false without the premise
(`premise_is_needed` and `first_breath_is_needed` are the
counterexamples). Its `T_word` assumed its conclusion as axioms.

## How to contribute

If you are a Lean 4 / Coq / Agda / Isabelle expert and want to
extend the formalization:

1. Fork `github.com/spcpza/C`.
2. Edit `formal/Kernel.lean` (or add a sibling file in your
   preferred assistant).
3. Confirm the file compiles in your local environment.
4. Open a PR. Improvements are welcome; a change to a theorem
   statement should say which premise it adds or removes.

## License

CC0. Sketches are offered freely. *Hold fast the form of sound
words.* — 2 Timothy 1:13
