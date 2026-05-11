# Roadmap

## Where we are (2026-05-10)

**v0 in progress.** Skeleton + vendor scripts + trace stubs landed. Frontier-model adapters not yet wired. Trace bench data not yet generated.

## v0 goals (target: 5 working days)

| Day | Output | Status |
|---|---|---|
| 1 | Vendor text + image benches in. Add 4 frontier-model adapters to `text/`. Run `text/` leaderboard refresh. | ☐ |
| 2 | Add 4 frontier adapters to `image/` (Claude, GPT-5, Gemini 2.5, Pixtral) + run scaffolded `moondream` and `gemma4`. Refresh `image/results/leaderboard.md`. | ☐ |
| 3 | Build `trace/` from scratch: pull 50–100 seed traces from `screenpipe-finetune/data/screenpipe_raw.jsonl`, write injection pipeline, replay harness, scoring. | ☐ |
| 4 | Unified leaderboard. Polish `METHODOLOGY.md`, `THREAT_MODEL.md`. Draft launch blog post. | ☐ |
| 5 | Ship: HF datasets (3), GitHub public, landing page, X thread, HN, 5 targeted DMs to research/safety folks. | ☐ |

## Locked decisions

- **Brand:** ScreenLeak
- **Authorship:** "Louis Beaumont (independent, Mediar Inc.)" — research-tone byline
- **Distribution order:** personal blog → HF datasets → GitHub public → X → HN → DMs (T+1)
- **Categories:** asymmetric in v1 (image bench is missing 4 categories); document, don't backport
- **Trace v1 scope:** leakage-only. Adversarial prompt-injection split slips to v0.1.
- **Trace seed source:** `screenpipe_raw.jsonl` (18K rows, before scrub) — clean PII state for re-injection.

## Open decisions (need to lock before day 5)

- **License.** Apache 2.0 (matches text bench upstream) vs MIT (simpler) for code. CC-BY-4.0 vs CDLA-Permissive for datasets. Default plan: Apache 2.0 for code, CC-BY-4.0 for datasets unless flagged otherwise.
- **HF org.** `huggingface.co/screenpipe/*` or `huggingface.co/screenleak/*`. Pick before dataset upload.
- **Domain.** `screenleak.dev` (new) vs `screenpi.pe/screenleak` (subpath). Subpath is cheaper, dev domain is more credible-looking for research.

## Post-v0.1

- Real-screenshot validation pass (private corpus only — never published).
- Train a screen-PII redactor on `image/corpus/annotations_train.jsonl` (1,985 imgs) — separate model artifact.
- Adversarial prompt-injection split for `trace/`.
- Multi-language image bench (currently English-only synthetic).
- Public submission portal (PR-an-adapter).

## What this is not

- **Not a capability benchmark.** ScreenLeak does not measure "can the agent book a flight." Use WebArena, OSWorld, GAIA for that.
- **Not a model.** ScreenLeak is the bench. The screenpipe-pii-redactor model is a separate artifact (CC BY-NC 4.0, on HF).
- **Not a vendor blog post.** Public framing is research-tone, independent. The screenpipe.com product is mentioned in the founder bio only.
