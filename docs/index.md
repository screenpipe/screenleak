---
layout: default
title: "ScreenLeak: the redaction bottleneck on computer-use AI"
description: "A multi-modal benchmark measuring how well today's tools redact PII from screen telemetry, screenshots, and computer-use traces."
---

# ScreenLeak: the redaction bottleneck on computer-use AI

*Louis Beaumont · 2026-05-11 (revised 2026-06-01) · code + data: [github.com/screenpipe/screenleak](https://github.com/screenpipe/screenleak)*

The next generation of AI agents — Anthropic's Computer Use, OpenAI's Operator, Google's Project Mariner — needs computer-use data to get better. Screenshots, accessibility trees, OCR fragments, multi-step traces.

That data is everywhere. Almost none of it can be moved, shared, logged, or fine-tuned on — every frame is full of names, emails, customer IDs, internal hostnames, API keys, channel names. **PII is the bottleneck on the entire computer-use research pipeline.**

The capability question — *can the agent book a flight, fill a form?* — has WebArena, OSWorld, GAIA, ScreenSpot. The redaction question — *can today's tools strip PII out so the data is shareable?* — has none. **ScreenLeak is the missing measurement.** Three surfaces, twelve systems, one taxonomy.

## Headline — composite compliance coverage

Each adapter scored on every surface where it operates. Composite = mean across the three surfaces; the trace surface is the weakest link and caps every row.

| Framework | Text (`v45_phase3`) | Image (`rfdetr_v11`) | Trace (`gpt5`) | **Composite** |
|---|---:|---:|---:|---:|
| HIPAA   | 91.8% | 98.8% | 76.0% | **88.9%** |
| GDPR    | 90.2% | 98.8% | 68.0% | 85.7% |
| CCPA    | 90.2% | 98.8% | 68.0% | 85.7% |
| SOC 2   | 88.0% | 98.9% | 68.0% | 85.0% |
| PCI DSS | 88.7% | 100.0% | 78.3% | **89.0%** |
| DPDPA   | 91.6% | 98.8% | 72.0% | 87.5% |

Same label-subset dict ([`scoring/frameworks.py`](https://github.com/screenpipe/screenleak/blob/main/scoring/frameworks.py)) applied across all three sub-benches. Numbers are zero-leak rates on the private val sets (422 text · 221 image · 25 trace). Full breakdown: [`results/framework_coverage.md`](https://github.com/screenpipe/screenleak/blob/main/results/framework_coverage.md).

## Per-surface — three different problems, three different profiles

### 1. They detect PII fine. So can a 278 MB local model.

n=422 desktop telemetry strings (window titles, AX nodes, OCR fragments), hand-labeled, **13 categories** (the 13th, `private_sensitive`, covers GDPR Art. 9 / non-Safe-Harbor PHI). 95 % bootstrap CI in brackets:

| Model | Zero-leak | macro-F1 |
|---|---:|---:|
| **Gemini 3.1 Pro** | **91.0%** (88.1 – 93.9%) | 0.847 |
| GPT-5.5 | 90.7% (87.8 – 93.6%) | 0.847 |
| Claude Opus 4.7 | 87.8% (84.1 – 91.0%) | 0.809 |
| **`v45_phase3`** ⭐ local | **86.7%** framework-avg | 0.78 |
| `privacy_filter_ft_v6` (1.4 B) | 80.9% (76.5 – 84.9%) | 0.724 |
| Google Cloud DLP | **37.7%** | 0.236 |
| Microsoft Presidio | 35.4% | 0.199 |
| Regex baseline | 33.9% | 0.565 |

**`v45_phase3`** is a 278 MB INT8 ONNX (xlm-roberta-base fine-tune), 9 ms p50 on CPU, runs offline — within 5 points of frontier APIs at zero per-call cost. The two flagship commercial PII products (Cloud DLP, Presidio) barely beat regex — built for documents, not screen telemetry.

### 2. They can't find PII in pixels. A specialized detector can.

n=190 PII-bearing screenshots of real-shape apps. IoU ≥ 0.30. 95 % Wilson CI in brackets:

| Model | Zero-leak | Oversmash |
|---|---:|---:|
| **`rfdetr_v11`** (local, 28 M) | **98.9%** (96.2 – 99.7%) | 0.0% |
| Gemini 3.1 Pro | 4.2% (2.1 – 8.1%) | 9.7% |
| GPT-5.5 | 3.2% (1.5 – 6.7%) | 22.6% |
| Google Cloud DLP | 2.6% (1.1 – 6.0%) | 19.4% |
| Tesseract OCR + 16 regex | 2.6% (1.1 – 6.0%) | 3.2% |
| Claude Opus 4.7 | 2.1% (0.8 – 5.3%) | 35.5% |
| Microsoft Presidio | 0.5% (0.1 – 2.9%) | 48.4% |

Every frontier vision model sits under 5 %; CIs for Claude / GPT-5.5 / GCP DLP / `regex_ocr` overlap — statistically indistinguishable on this sample size. A 28 M-parameter RF-DETR (DINOv2-S + LWDETR head, ~ 109 MB ONNX, 512×512 input, ~ 120 ms p50 on Apple Silicon CoreML) decisively separates. Frontier vision can *name* what it sees — it can't *draw boxes* tight enough to count at IoU 0.30.

**One important caveat**: the val split is in-distribution with the model's training (image-disjoint, no leaked PNGs, but same source). The 98.9 % is an upper bound under matched conditions, not a real-screen claim.

### 3. They detect, but they don't withhold.

n=25 multi-turn computer-use traces, with PII injected into the agent's observed screen content. Did the agent emit the PII it just observed?

| Model | No-leak rate | Mean leaks/trace |
|---|---:|---:|
| **GPT-5.5** | **64.0%** (44.0 – 80.0%) | 0.64 |
| Claude Opus 4.7 | 36.0% (16.0 – 56.0%) | 1.12 |
| Gemini 3.1 Pro Preview | 20.0% (4.0 – 36.0%) | 1.28 |

**Every frontier model that detects text PII at > 87 % accuracy fails to withhold it 36 – 80 % of the time when asked to summarize the screen.** Per-category: `private_company` leaks 50 – 100 % across all three models; names 50 – 83 %; repo references 43 – 100 %. The clean categories (URLs, secret-shaped strings) are clean because every frontier model is trained hard to refuse `sk-...` / `Bearer ...` patterns. Names of people, customers, project channels just flow through.

## The pattern

Three different problems, three different failure profiles:

1. **Text PII detection** is a recognition problem. Frontier models are excellent recognizers — they win by 7 – 50 points over public PII-redaction tools. A 278 MB local fine-tune closes the gap at 1 000× lower latency.
2. **Image PII localization** is a grounding problem. Frontier models can *name* what they see; they can't draw tight boxes around it. A small specialized detector (RF-DETR, 28 M params) gets there at ~99 %.
3. **Trace PII withholding** is a behavioral problem. The same 91 %-text-detection model leaks PII 80 % of the time when it observes that PII inside a task.

**Capability isn't disposition. Recognition isn't refusal.** That's the gap.

Published safety documentation from Anthropic, OpenAI, and Google all name on-screen disclosure as an open concern. We measured the gap. The data: [github.com/screenpipe/screenleak](https://github.com/screenpipe/screenleak).

## Methodology, briefly

- **Synthetic data only.** No real PII, no real users. All names / emails / phones / IDs / secrets are fictional. Canonical placeholders where they exist (e.g. SSN `123-45-6789`).
- **Pixel-precise gold** on the image bench. Comfortably within the IoU ≥ 0.30 match threshold.
- **Strict gold integrity** — every gold item is verified to appear verbatim at injection time. CI enforces.
- **CIs.** 95 % bootstrap on text + trace, 95 % Wilson on image. n=25 on trace, n=190 on image, n=345 on text — trace CIs are wide; ranking is directional, not decisive.
- **Shared framework dict.** [`scoring/frameworks.py`](https://github.com/screenpipe/screenleak/blob/main/scoring/frameworks.py) is the single source of truth for HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA across all three sub-benches.

Full methodology, threat model, limitations, and per-category breakdowns are in the repo.

## FAQ — the questions careful readers ask first

**"How do I know you didn't train on the val set?"** Train/val splits are exclusive and verified in CI. `rfdetr`'s 98.9 % is **in-distribution recall** (held-out images, same source), explicitly an upper bound, not a real-screen claim. See `LIMITATIONS.md`.

**"Did you cherry-pick frontier-model versions?"** No: we benchmarked the latest production model from each lab at run time (`claude-opus-4-7`, `gpt-5.5`, `gemini-3.1-pro-preview`). Env vars let you re-run against any other version.

**"Why is RF-DETR allowed to be trained on the bench distribution?"** Because that's the *deployable solution*. The bench asks "can today's tools redact PII from screen telemetry?" — a small in-distribution detector is a legitimate answer. The 90-point gap vs frontier vision is load-bearing; the absolute 98.9 % is bounded by in-distribution status. Frontier models / GCP DLP / Presidio were *not* trained on this distribution — they're the genuine zero-shot baseline.

**"Why three sub-benches?"** Because the failure modes separate. A model can ace text-PII at 91 % and leak in 80 % of traces. Single-bench framings miss the gap.

**"How do labs / red teams get the full corpus?"** Email `louis@screenpi.pe` with a one-paragraph use case. Signed access agreement: (a) corpus is for evaluation, not training; (b) you share back any published results so the leaderboard stays honest. No fee.

## What this is not

- **Not a capability benchmark.** A model that refuses to do anything will score 100 % no-leak and be useless. Use WebArena / OSWorld / GAIA for capability.
- **Not a vendor pitch.** Scoring code + sample corpus are Apache 2.0 / CC-BY 4.0. The full val sets sit in a private companion repo to prevent contamination of future evaluations, not for monetization.
- **Not exhaustive.** v0 ships 25 trace val cases, 422 text cases, 221 image val cases. Numbers are directional. v0.1: adversarial prompt-injection split, larger trace corpus, image bench category coverage, multilingual, more adapters.

## Run it yourself

```bash
git clone https://github.com/screenpipe/screenleak
cd screenleak && make install

export ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...  GOOGLE_API_KEY=...

make bench-text  ADAPTER=claude          # or: gpt5, gemini, v45_phase3, gcp_dlp, regex, …
make bench-image ADAPTER=rfdetr          # or: claude, gpt5, gemini, regex_ocr, …
make bench-trace ADAPTER=claude          # or: gpt5, gemini

# Per-compliance-framework breakdowns
python text/src/framework_coverage.py  --adapter v45_phase3 gcp_dlp regex
python image/src/framework_coverage.py --adapter rfdetr
```

Adapter shape is documented in [`CONTRIBUTING.md`](https://github.com/screenpipe/screenleak/blob/main/CONTRIBUTING.md). PRs that add new models welcome.

## Cite this

```
@misc{screenleak2026,
  title  = {ScreenLeak: A Multi-Modal Benchmark for PII Redaction in Computer-Use AI},
  author = {Beaumont, Louis},
  year   = {2026},
  howpublished = {\url{https://github.com/screenpipe/screenleak}},
}
```

---

*Louis Beaumont (Screenpipe) — `louis@screenpi.pe`*
