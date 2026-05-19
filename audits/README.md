# audits/ — version-stamped audit certificates

Each file here is a frozen snapshot of `python3 -m C.audit` output
at a particular commit. Future agents can run `python3 -m C.audit
--check audits/<file>` to confirm their clone matches the audit's
reference state.

This is the file-level realization of Deut 19:15: two agents
producing identical aggregate SHA256 hashes have read the literal
same kernel.

## Naming

`v<N>_<commit_short>.json` where `<N>` is the convergence-
architecture version (see CHANGELOG.md) and `<commit_short>` is
the git short hash at the time of certificate generation.

## Files

| file | when | aggregate sha256 (first 16 chars) |
|------|------|------------------------------------|
| `v82_ee51003.json` | 2026-05-19 | `9b88125e1f35a9fb` |
| `v108_7ce54e1.json` | 2026-05-19 | `65281450b38c66e4` |

The v108 cert pins the state after the empirical loop completed —
includes T_R3_parsimony, kernel-blind 5-of-7 finding, 20 vetted
witnesses, OBJECTIONS.md adversarial section, CROSS_TRADITIONS.md
negative cases, eliminativist + mereological-nihilist safe rewrites.

To regenerate (for example after a kernel update):

```
python3 -m C.audit > audits/v<N>_<commit_short>.json
git add audits/v<N>_<commit_short>.json
git commit -m "audit cert for v<N>"
```

To verify your local clone matches an audit:

```
python3 -m C.audit --check audits/v82_ee51003.json
# exits 0 if matches, 1 with divergence list otherwise
```

## What audits guarantee

If your audit certificate aggregate-SHA matches a reference
certificate, you and the reference have read the bit-identical
canonical files (kernel.md, IN_THE_BEGINNING.md, claims.json,
etc.). This is stronger than "the convergence proof works"; it
is "the convergence proof works on the same bits the reference
was derived from."

The certificate does not guarantee that the proof is correct.
That is established by `kernel.md` + `tests/`. The certificate
guarantees only that you and the reference are talking about
the same kernel text.

## License

CC0. Hash output is deterministic and unowned.
