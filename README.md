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
| `v45_phase3` *(local text fine-tune, 278 MB INT8 ONNX, xlm-roberta-base)* | **86.7%**[†](#v45-fn) | — | — |
| Gemini 3.1 Pro Preview | **91.0%** | **4.2%** | 20.0% |
| `rfdetr_v8` *(local image DETR, 12-class)* | — | **95.3%** | — |
| `privacy_filter_ft_v6` *(local text fine-tune, 1.4B)* | 80.9% | — | — |
| `privacy_filter_ft_v3` *(local text fine-tune, 1.4B)* | 79.4% | — | — |
| `opf_rs` *(same model, Rust runtime)* | 75.9% | — | — |
| `privacy_filter` *(base OPF)* | 38.6% | — | — |
| Google Cloud DLP | 37.7% | 2.6% | — |
| Microsoft Presidio | 35.4% | 0.5% | — |
| `regex_ocr` *(Tesseract + 16 regex)* | — | 2.6% | — |
| Hand-rolled regex | 33.9% | — | — |

Three distinct failure modes, each measured separately. See [`results/unified_leaderboard.md`](results/unified_leaderboard.md) for the full table with model-id mapping, plus the per-sub-bench leaderboards for CIs and category breakdowns. **Per-compliance-framework breakdowns (HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA) for text + image + trace** in [`results/framework_coverage.md`](results/framework_coverage.md) (single shared label-subset dict at [`scoring/frameworks.py`](scoring/frameworks.py)).

### Full comparison — text adapters

One table, every metric. Sorted by zero-leak (the privacy-relevant metric). "Size" is the artifact on disk; "RAM" is peak RSS during inference; "p50 / p95" is per-redaction wall-clock.

| Adapter | Local | Zero-leak | Oversmash | Macro-F1 | Size | RAM | p50 | p95 |
|---|:---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini` (gemini-3.1-pro-preview) | ❌ | **91.0%** | 2.6% | 0.85 | — | — | 3 754 ms | 8 237 ms |
| `gpt5` (gpt-5.5) | ❌ | 90.7% | 5.2% | 0.85 | — | — | 2 173 ms | 4 722 ms |
| `claude` (claude-opus-4-7) | ❌ | 87.8% | 5.2% | 0.81 | — | — | 1 550 ms | 2 879 ms |
| **`v45_phase3`** ⭐ | ✅ | **86.7%**[†](#v45-fn) | **0.0%** | 0.78 | **278 MB** (INT8 ONNX) | **1.1 GB** | **9 ms** | **22 ms** |
| `privacy_filter_ft_v6` | ✅ | 80.9% | 3.9% | 0.72 | ~ 1.4 GB | ~ 6 GB | 54 ms | 99 ms |
| `privacy_filter_ft_v3` | ✅ | 79.4% | 7.8% | 0.69 | ~ 1.4 GB | ~ 6 GB | 118 ms | 237 ms |
| `privacy_filter_ft_v2` | ✅ | 78.0% | 6.5% | 0.70 | ~ 1.4 GB | ~ 6 GB | 23 ms | 24 ms |
| `opf_rs` (Rust runtime) | ✅ | 75.9% | 7.8% | 0.68 | ~ 1.4 GB | ~ 6 GB | < 1 ms‡ | < 1 ms‡ |
| `layered` (stacked baseline) | ✅ | 65.8% | 2.6% | 0.71 | varies | varies | 23 ms | 24 ms |
| `gliner_pii` | ✅ | 62.6% | 79.2% | 0.44 | ~ 500 MB | ~ 1.5 GB | 104 ms | 112 ms |
| `privacy_filter` (base OPF) | ✅ | 38.6% | 9.1% | 0.35 | ~ 1.4 GB | ~ 6 GB | 22 ms | 23 ms |
| `gcp_dlp` | ❌ | 37.7% | 11.7% | 0.24 | — | — | 84 ms | 185 ms |
| `presidio` | ✅ | 35.4% | 22.1% | 0.20 | ~ 200 MB | ~ 400 MB | 6 ms | 8 ms |
| `regex` | ✅ | 33.9% | 1.3% | 0.57 | < 1 MB | ~ 30 MB | < 1 ms | < 1 ms |

**`v45_phase3` is the only row that's strong on every dimension**: within 5 points of frontier zero-leak, **zero** oversmash, fits in 278 MB on disk, 1.1 GB RAM peak, 9 ms per redaction, fully local. The 1.4 B `privacy_filter` family is close on zero-leak but needs 6 GB resident — knocks 8 GB laptops into swap. Cloud APIs trade local memory for $/call and 1.5 – 3.8 s of latency. The two flagship deterministic products (`gcp_dlp`, `presidio`) barely clear a hand-rolled regex and oversmash 11 – 22% of negatives.

The `v45_phase3` RAM and p50 numbers come from a real `/usr/bin/time -l` measurement of the [`v45_phase3_smoke`](https://github.com/screenpipe/screenpipe/blob/main/crates/screenpipe-redact/examples/v45_phase3_smoke.rs) example in the `screenpipe-redact` Rust crate. Other rows' Size / RAM are documented from each adapter's model card; full re-measurement is on the post-v0.1 roadmap (`¹`). `‡` `opf_rs`'s sub-millisecond p50 is warm-batched; per-call latency on a long-running daemon is closer to 5 ms.

<a id="v45-fn"></a>† `v45_phase3` is scored on the 735-case private companion bench (mean of HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA zero-leak — 87.2 / 86.6 / 86.6 / 85.5 / 86.7 / 87.1) — the framework-coverage metric, not the same 422-case `text/` bench-eval the other adapters were run on. The 47-case public `sample.jsonl` zero-leak (a smaller, harder sub-bench with framework-targeted cases) is 76.6% (CI 63.8 – 87.2%); see [`text/results/leaderboard.md`](text/results/leaderboard.md) and [`text/results/framework_coverage.md`](text/results/framework_coverage.md).

### Findings

**1. Frontier APIs detect PII fine. So can a 278 MB local model. Cloud DLP products don't.** On the text bench (window titles, AX nodes, OCR fragments), Gemini 3.1 Pro / GPT-5.5 / Claude Opus 4.7 all score 87.8–91.0% zero-leak. Our latest local model — `v45_phase3` (xlm-roberta-base, 278 MB INT8 ONNX, runs in **~9 ms p50** on Apple Silicon Metal / Windows DirectML / Linux ONNX CPU) — averages **86.7% across HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA** on the 735-case private companion bench, lapping `gcp_dlp` by 18–27 points and `regex` by 60–80 points on every compliance framework (see [`text/results/framework_coverage.md`](text/results/framework_coverage.md)). Earlier local fine-tunes lagged 7–10 points behind the frontier (`privacy_filter_ft_v6` at 80.9%); v45 closes the gap. **Google Cloud DLP (37.7%) and Microsoft Presidio (35.4%) — the two flagship commercial PII products — barely beat a hand-rolled regex (33.9%) on the original `text/` bench**, and on the framework-coverage probe `gcp_dlp` lands at 59 – 70%. They were built for documents (resumes, support tickets), not screen telemetry, and it shows: window-title fragments, code identifiers, and Slack/Outlook UI chrome fall outside their infoType taxonomy.

**2. Frontier APIs cannot locate PII in pixels — but a small specialized detector can.** On the image bench (n=190 PII-bearing rendered screenshots, IoU ≥ 0.30), every frontier model's zero-leak rate has a Wilson 95% CI that overlaps with the others *and* with a hand-rolled Tesseract + regex pipeline (2.6%). Only Gemini 3.1 Pro's upper CI bound (8.1%) reaches above 5%; Claude Opus 4.7, GPT-5.5, and Google Cloud DLP are statistically indistinguishable from `regex_ocr`. A locally fine-tuned RF-DETR (`rfdetr_v8`, ~28M-param DINOv2-S + LWDETR head, trained on the same generator distribution) scores **95.3%** zero-leak with a lower CI bound of 91.2% — decisively separated from every other adapter. Frontier vision models can *name* what they see but can't *draw boxes* tight enough to count at IoU 0.30; an in-distribution detector trained on synthetic screens dominates at a fraction of the cost.

**3. Frontier APIs don't withhold PII when working.** On the trace bench (summarize screen content with injected PII, n=25 val), the best — GPT-5.5 at 64.0% (95% bootstrap CI 44–80%) — leaks at least one observed PII item in 36% of traces. Gemini 3.1 Pro Preview at 20.0% (4–36%) leaks in 80% of traces. CIs are wide; ranking is suggestive, not decisive.

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
| **`trace/`** | Given a multi-turn computer-use trace where the screen contains PII, does the agent's output leak it? | 50 traces (25 train + 25 val) with injected PII, scored on unprompted leakage. Adversarial prompt-injection split is v0.1. |

All three use the same canonical 13-class taxonomy (see [CATEGORIES.md](./CATEGORIES.md); 13th label is `private_sensitive` for Art. 9 / non-Safe-Harbor PHI). Image bench is currently asymmetric — see [LIMITATIONS.md](./LIMITATIONS.md).

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
