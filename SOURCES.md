# Sources

Provenance for the assets shipped in this repo.

## What's here

- **Scoring code** — text / image / trace scorers + the shared framework-coverage probes. Apache 2.0.
- **Public sample** per surface — a small slice of each sub-bench's gold set, included so anyone can run an adapter end-to-end and verify the scoring kernel. CC BY 4.0.
- **Adapters** — wrappers around the models and APIs we benchmark. Apache 2.0.
- **Documentation** — methodology, threat model, categories, limitations, citation.

## What's not here, and where it lives

| Asset | Location |
|---|---|
| Full text bench val set | Private companion repo |
| Full image bench val set + render pipeline | Private companion repo |
| Full trace bench val set + replay infrastructure | Private companion repo |
| `screenpipe/pii-redactor` model weights | HuggingFace: `screenpipe/pii-redactor` (CC BY-NC 4.0) |
| `screenpipe/pii-image-redactor` weights | HuggingFace: `screenpipe/pii-image-redactor` |
| OPF Rust runtime | Separate engineering artifact, separate launch |

The full val sets are kept private to keep the leaderboard uncontaminated and the moat intact — training on the generator would game the bench trivially. Researchers running serious evaluations can request access at `louis@screenpi.pe`.

## What's intentionally never here

- Any real user data. All PII in this repo is synthetic / fictional.
- The screenpipe app's internal recording corpus. Out of scope for any public artifact.
- Training mixtures, seed pools, generator implementations.
