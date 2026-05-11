# ScreenLeak

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC_BY_4.0-lightgrey.svg)](LICENSE-DATA)
[![ci](https://img.shields.io/badge/ci-pytest%20%2B%20ruff-black)](.github/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

> A multi-modal benchmark measuring **how well today's tools redact PII from screen telemetry, rendered screenshots, and multi-step computer-use traces** — so the data substrate for the next generation of computer-use AI can actually move.

Blog: [screenpipe.github.io/screenleak](https://screenpipe.github.io/screenleak/) · Contact: `louis@screenpi.pe`

## Headline results (v0)

| Model | Text zero-leak | Image zero-leak | Trace no-leak |
|---|---:|---:|---:|
| **GPT-5.5** | 90.7% | 3.2% | **64.0%** |
| Claude Opus 4.7 | 87.8% | 2.1% | 36.0% |
| Gemini 3.1 Pro Preview | **91.0%** | **4.2%** | 20.0% |
| `rfdetr_v8` *(local image DETR, 12-class)* | — | **95.3%** | — |
| `privacy_filter_ft_v3` *(local text fine-tune, 1.4B)* | 79.4% | — | — |
| `opf_rs` *(same model, Rust runtime)* | 75.9% | — | — |
| `privacy_filter` *(base OPF)* | 38.6% | — | — |
| Google Cloud DLP | 37.7% | 2.6% | — |
| Microsoft Presidio | 35.4% | 0.5% | — |
| `regex_ocr` *(Tesseract + 16 regex)* | — | 2.6% | — |
| Hand-rolled regex | 33.9% | — | — |

Three distinct failure modes, each measured separately. See [`results/unified_leaderboard.md`](results/unified_leaderboard.md) for the full table with model-id mapping, plus the per-sub-bench leaderboards for CIs and category breakdowns.

### Findings

**1. Frontier APIs detect PII fine. Cloud DLP products don't.** On the text bench (window titles, AX nodes, OCR fragments), Gemini 3.1 Pro / GPT-5.5 / Claude Opus 4.7 all score 87.8–91.0% zero-leak, beating the strongest local model (`privacy_filter_ft_v3` at 79.4%) by 8–12 points. **Google Cloud DLP (37.7%) and Microsoft Presidio (35.4%) — the two flagship commercial PII products — barely beat a hand-rolled regex (33.9%).** They were built for documents (resumes, support tickets), not screen telemetry, and it shows: window-title fragments, code identifiers, and Slack/Outlook UI chrome fall outside their infoType taxonomy.

**2. Frontier APIs cannot locate PII in pixels — but a small specialized detector can.** On the image bench (n=221 rendered screenshots, IoU ≥ 0.30), the best frontier model — Gemini 3.1 Pro at 4.2% — barely edges a hand-rolled regex + Tesseract OCR pipeline (2.6%). Claude Opus 4.7 (2.1%) and **Google Cloud DLP (2.6%)** are statistically indistinguishable from `regex_ocr`. **No frontier model breaks 5% zero-leak; Google's commercial DLP product doesn't either.** A locally fine-tuned RF-DETR (`rfdetr_v8`, ~28M-param DINOv2-S + LWDETR head, trained on the same generator distribution) scores **95.3%** — a 90-point gap. The pattern: frontier vision models can *name* what they see but can't *draw boxes* tight enough to count; an in-distribution detector trained on synthetic screens dominates at a fraction of the cost.

**3. Frontier APIs don't withhold PII when working.** On the trace bench (summarize screen content with injected PII), the best — GPT-5.5 at 64.0% — leaks at least one observed PII item in 36% of traces. The worst, Gemini 3.1 Pro Preview at 20.0% no-leak, leaks in 80%.

**The pattern:** capability (text bench) ≠ pixel grounding (image bench) ≠ disposition (trace bench). A model that nails text PII detection at 91% can still leak it 80% of the time when it observes that PII inside a task.

See [`THREAT_MODEL.md`](THREAT_MODEL.md) for what counts as a leak. See [`LIMITATIONS.md`](LIMITATIONS.md) for caveats — notably that `rfdetr` was trained on the same synthetic-screen generator pipeline its val split comes from (held-out images, same distribution), so its 95.3% is an upper bound under matched conditions, not a real-world out-of-distribution claim.

---

## Why this exists

Existing computer-use benchmarks (WebArena, OSWorld, AgentBench, GAIA, Mind2Web, ScreenSpot) measure **capability** — can the agent book a flight, fill a form, navigate a site? They don't measure what the agent **discloses** while doing the task.

Anthropic's computer-use safety post (Oct 2024), OpenAI's Operator system card, and Google's Mariner safety docs all flag the same open question: when an agent screenshots the user's screen, what does it transcribe into chats? What does it leak under prompt injection embedded in on-screen text? What survives across a multi-turn workflow?

ScreenLeak is the missing measurement.

## The three sub-benches

| Sub-bench | What it measures | Corpus |
|---|---|---|
| **`text/`** | Given a desktop telemetry string (window title, AX node, OCR fragment), find PII spans | 422 hand-crafted cases, 13 categories, multilingual + adversarial splits |
| **`image/`** | Given a rendered screen, find pixel regions containing PII | 2,206 synthetic screenshots across 9 real-app templates with pixel-perfect DOM-extracted bboxes |
| **`trace/`** | Given a multi-turn computer-use trace where the screen contains PII, does the agent's output leak it? | 50–100 traces with injected PII, scored on unprompted leakage + adversarial prompt-injection |

All three use the same canonical 12-class taxonomy (see [CATEGORIES.md](./CATEGORIES.md)). Image bench is currently asymmetric — see [LIMITATIONS.md](./LIMITATIONS.md).

## Headline claim

> **ScreenLeak is the first public benchmark to measure sensitive-information disclosure in computer-use vision and agent models.**

## What's in this repo

This is the **public companion** to ScreenLeak. It contains:

- Full **scoring code** for all three sub-benches (`text/src/score.py`, `image/src/score.py`, `trace/src/score.py` + `trace/src/replay.py`).
- Every **adapter** we benchmarked: Claude, GPT-5.5, Gemini, Google Cloud DLP, Microsoft Presidio, GLiNER, `privacy_filter` family, RF-DETR, regex baselines (across all surfaces).
- **Methodology**, **threat model**, **categories**, **limitations**, **citation**.
- A **30-row sample corpus per surface** so you can run any adapter end-to-end:
  - `text/data/sample.jsonl` — 36 cases across 12 categories
  - `image/corpus/sample/` — 30 rendered screenshots + DOM-extracted gold bboxes
  - `trace/data/injected_sample.jsonl` — 5 multi-turn computer-use traces

The **full corpus** (422 text + 221 val image + 50-trace val set) and the **synthetic-data generators** (`gen_specs.py`, `pii_pool.py`, `inject.py`, `build_seeds.py`, `templates/`) live in a private companion repo. Generators are how new benchmark versions get built and how the leaderboard stays uncontaminated by training on it — see `LIMITATIONS.md` for the rationale.

Researchers running serious evaluations should contact `louis@screenpi.pe` for access to the full corpus.

## Run an adapter on the sample

```bash
# 0. install
make install

# 1. set API keys for whichever adapters you want
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...

# 2. run a single adapter against the sample
make bench-text  ADAPTER=claude          # or: gpt5, gemini, gcp_dlp, regex, …
make bench-image ADAPTER=rfdetr          # or: claude, gpt5, gemini, regex_ocr, …
make bench-trace ADAPTER=claude          # or: gpt5, gemini
```

Headline leaderboard numbers in this repo are computed on the **full** corpus (in the private repo); sample-corpus runs are for adapter-validation and onboarding, not for re-ranking models.

## Cite this

See [CITATION.bib](./CITATION.bib).

## Contact

`louis@screenpi.pe`
