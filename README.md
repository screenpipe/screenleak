# ScreenLeak

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data-CC_BY_4.0-lightgrey.svg)](LICENSE-DATA)
[![ci](https://img.shields.io/badge/ci-pytest%20%2B%20ruff-black)](.github/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

> **A multi-modal benchmark measuring how well today's tools redact PII from screen telemetry, rendered screenshots, and multi-step computer-use traces.**

Blog: [screenpipe.github.io/screenleak](https://screenpipe.github.io/screenleak/) · Contact: `louis@screenpi.pe`

## Headline — composite framework coverage (text · image · trace)

Each adapter is scored on every surface where it operates. The composite is the mean across surfaces; the trace surface is the weakest link and caps every row.

| Framework | Text<br>(`v45_phase3`) | Image<br>(`rfdetr_v11`) | Trace<br>(`gpt5`) | **Composite** |
|---|---:|---:|---:|---:|
| HIPAA   | 91.8% | 98.8% | 76.0% | **88.9%** |
| GDPR    | 90.2% | 98.8% | 68.0% | 85.7% |
| CCPA    | 90.2% | 98.8% | 68.0% | 85.7% |
| SOC 2   | 88.0% | 98.9% | 68.0% | 85.0% |
| PCI DSS | 88.7% | 100.0% | 78.3% | **89.0%** |
| DPDPA   | 91.6% | 98.8% | 72.0% | 87.5% |

Single shared label-subset dict ([`scoring/frameworks.py`](scoring/frameworks.py)) applies across all three surfaces. Numbers are zero-leak rates on the private val sets (422 text · 221 image · 25 trace) — re-runnable from the public sample with the same probes. Full unified breakdown: [`results/framework_coverage.md`](results/framework_coverage.md).

## Three sub-benches

| Bench | Question | Corpus |
|---|---|---|
| [`text/`](text/) | Find PII in window titles / AX nodes / OCR fragments | 422 cases · 13 labels · multilingual + adversarial splits |
| [`image/`](image/) | Find pixel regions of PII in rendered screens | Synthetic screenshots · 9 app templates · pixel-precise gold |
| [`trace/`](trace/) | Does the agent leak PII it observes inside a task? | 50 traces (25 train + 25 val) with injected PII |

All three use the same 13-label taxonomy ([`CATEGORIES.md`](CATEGORIES.md)).

## Three failure modes — text adapters, full comparison

Zero-leak alone is half the picture. Local size + RAM + latency are the other half. The `v45_phase3` row is the only one strong on every dimension.

| Adapter | Local | Zero-leak | Oversmash | macro-F1 | Size | RAM | p50 |
|---|:---:|---:|---:|---:|---:|---:|---:|
| `gemini` (gemini-3.1-pro) | ❌ | **91.0%** | 2.6% | 0.85 | — | — | 3 754 ms |
| `gpt5` (gpt-5.5) | ❌ | 90.7% | 5.2% | 0.85 | — | — | 2 173 ms |
| `claude` (claude-opus-4-7) | ❌ | 87.8% | 5.2% | 0.81 | — | — | 1 550 ms |
| **`v45_phase3`** ⭐ | ✅ | **86.7%** | **0.0%** | 0.78 | **278 MB** | **1.1 GB** | **9 ms** |
| `privacy_filter_ft_v6` | ✅ | 80.9% | 3.9% | 0.72 | ~ 1.4 GB | ~ 6 GB | 54 ms |
| `opf_rs` / privacy_filter family | ✅ | 38 – 80% | 4 – 10% | 0.35 – 0.72 | ~ 1.4 GB | ~ 6 GB | 1 – 120 ms |
| `gliner_pii` | ✅ | 62.6% | 79.2% | 0.44 | ~ 500 MB | ~ 1.5 GB | 104 ms |
| `gcp_dlp` | ❌ | 37.7% | 11.7% | 0.24 | — | — | 84 ms |
| `presidio` | ✅ | 35.4% | 22.1% | 0.20 | ~ 200 MB | ~ 400 MB | 6 ms |
| `regex` | ✅ | 33.9% | 1.3% | 0.57 | < 1 MB | ~ 30 MB | < 1 ms |

`v45_phase3` peak RSS measured via `cargo run --release --example v45_phase3_smoke --features onnx-cpu`. Other adapters' size / RAM from each model's card.

## Findings

**1. A 278 MB local model matches frontier APIs on text. Cloud DLP products don't.** On the 422-case text bench, Gemini / GPT-5.5 / Claude all score 87.8 – 91.0 % zero-leak. `v45_phase3` averages 90 % across compliance frameworks at 9 ms p50 on CPU. Google Cloud DLP (37.7 %) and Microsoft Presidio (35.4 %) barely beat a hand-rolled regex (33.9 %) — they were built for documents, not screen telemetry.

**2. Frontier vision can't draw boxes. A small specialized detector can.** On 190 PII-bearing screenshots at IoU ≥ 0.30, every frontier vision API sits below 5 % zero-leak with CIs that overlap each other and the Tesseract+regex baseline. A locally fine-tuned RF-DETR-Nano (28 M params, ~109 MB, 512×512 input) hits **98.9 %** with a lower CI bound of 96.2 % — decisively separated.

**3. Frontier APIs don't withhold PII when working.** On 25 multi-turn traces, the strongest (GPT-5.5 at 64.0 %, CI 44 – 80 %) still leaks at least one observed PII item in 36 % of traces. Gemini at 20 % leaks in 80 % of traces.

**The pattern:** capability ≠ pixel-grounding ≠ disposition. A model nailing text detection at 91 % can still leak PII 80 % of the time when it observes that PII inside a task. See [`THREAT_MODEL.md`](THREAT_MODEL.md) for what counts as a leak, [`LIMITATIONS.md`](LIMITATIONS.md) for caveats (notably: `rfdetr`'s val is in-distribution with its training — held-out images, same source).

## What's in this repo

- **Scoring code** — `text/src/score.py`, `image/src/score.py`, `trace/src/score.py` + `trace/src/replay.py`. Shared framework probe at [`scoring/frameworks.py`](scoring/frameworks.py).
- **Every adapter benchmarked** — Claude, GPT-5.5, Gemini, GCP DLP, Presidio, GLiNER, `privacy_filter` family, RF-DETR, regex baselines.
- **Methodology / threat model / categories / limitations / citation.**
- **Public sample per surface** so any adapter can be run end-to-end without the full corpus:
  - `text/data/sample.jsonl` — 51 cases (incl. PHI / PCI / Art. 9 / multilingual tasters)
  - `image/corpus/sample/` — 30 rendered screenshots + DOM-extracted gold bboxes
  - `trace/data/injected_sample.jsonl` — 5 multi-turn computer-use traces

The **full val sets** and the data pipelines that produce them live in a private companion repo — to keep the leaderboard uncontaminated by training-on-the-bench and to preserve the moat. Researchers running serious evaluations can request access at `louis@screenpi.pe`.

## Run an adapter on the sample

```bash
make install
export ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...  GOOGLE_API_KEY=...

make bench-text  ADAPTER=claude          # or: gpt5, gemini, v45_phase3, gcp_dlp, regex, …
make bench-image ADAPTER=rfdetr          # or: claude, gpt5, gemini, regex_ocr, …
make bench-trace ADAPTER=claude          # or: gpt5, gemini
```

Headline leaderboard numbers are computed on the full private corpus; sample-corpus runs are for adapter validation and onboarding, not re-ranking.

## Cite this

See [CITATION.bib](CITATION.bib).

## Contact

`louis@screenpi.pe`
