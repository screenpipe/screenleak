# Leaderboard

Sorted by **zero-leak rate** (the % of cases with PII where ALL gold spans were caught — the metric that matters for privacy use cases). 95% bootstrap CI in brackets.

| Adapter | Zero-leak (95% CI) | Oversmash | Easy | Medium | Hard | Macro-F1 | Micro-F1 | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini` | 91.0% (88.1%-93.9%) | 2.6% | 91% | 90% | 98% | 0.847 | 0.919 | 3754 | 8237 |
| `gpt5` | 90.7% (87.8%-93.6%) | 5.2% | 91% | 90% | 93% | 0.847 | 0.905 | 2173 | 4722 |
| `claude` | 87.8% (84.1%-91.0%) | 5.2% | 86% | 87% | 96% | 0.809 | 0.867 | 1550 | 2879 |
| `v45_phase3` ⭐ local | 76.6% (63.8%-87.2%) | 0.0% | — | 77% | — | 0.780 | 0.845 | 9 | 22 |
| `privacy_filter_ft_v6` | 80.9% (76.5%-84.9%) | 3.9% | 91% | 80% | 75% | 0.724 | 0.854 | 54 | 99 |
| `privacy_filter_ft_v3` | 79.4% (75.1%-83.8%) | 7.8% | 91% | 79% | 70% | 0.689 | 0.823 | 118 | 237 |
| `privacy_filter_ft_v2` | 78.0% (73.6%-82.3%) | 6.5% | 86% | 78% | 73% | 0.698 | 0.829 | 23 | 24 |
| `opf_rs` | 75.9% (71.6%-80.6%) | 7.8% | 86% | 77% | 61% | 0.677 | 0.785 | 0 | 0 |
| `layered` | 65.8% (60.9%-71.0%) | 2.6% | 63% | 69% | 50% | 0.712 | 0.765 | 23 | 24 |
| `gliner_pii` | 62.6% (57.1%-67.5%) | 79.2% | 74% | 61% | 64% | 0.444 | 0.526 | 104 | 112 |
| `privacy_filter` | 38.6% (33.6%-43.8%) | 9.1% | 49% | 35% | 52% | 0.346 | 0.526 | 22 | 23 |
| `gcp_dlp` | 37.7% (32.8%-42.9%) | 11.7% | 43% | 34% | 55% | 0.236 | 0.368 | 84 | 185 |
| `presidio` | 35.4% (30.4%-40.3%) | 22.1% | 51% | 34% | 32% | 0.199 | 0.430 | 6 | 8 |
| `regex` | 33.9% (28.7%-38.8%) | 1.3% | 31% | 37% | 18% | 0.565 | 0.526 | 0 | 0 |

## Per-category recall

| Adapter | account_number | private_address | private_channel | private_company | private_date | private_email | private_handle | private_id | private_person | private_phone | private_repo | private_url | secret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemini` | 0.00 | 1.00 | 1.00 | 0.89 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.90 | 0.75 | 0.79 |
| `gpt5` | 0.00 | 1.00 | 1.00 | 0.91 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | 1.00 | 0.80 | 0.79 |
| `claude` | 0.00 | 1.00 | 1.00 | 0.92 | 1.00 | 1.00 | 1.00 | 0.86 | 0.90 | 1.00 | 1.00 | 0.70 | 0.93 |
| `v45_phase3` | — | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 | 0.73 | 0.93 | 0.67 | 1.00 | 1.00 | 0.33 |
| `privacy_filter_ft_v6` | 0.00 | 0.83 | 0.55 | 0.86 | 0.00 | 0.98 | 0.95 | 0.95 | 0.87 | 0.92 | 0.68 | 1.00 | 0.79 |
| `privacy_filter_ft_v3` | 0.00 | 0.75 | 0.65 | 0.81 | 0.00 | 1.00 | 0.95 | 0.91 | 0.86 | 0.92 | 0.68 | 1.00 | 0.79 |
| `privacy_filter_ft_v2` | 0.00 | 0.83 | 0.50 | 0.79 | 0.00 | 1.00 | 0.91 | 0.91 | 0.84 | 0.92 | 0.63 | 1.00 | 0.79 |
| `opf_rs` | 0.00 | 0.83 | 0.65 | 0.81 | 0.00 | 0.94 | 0.95 | 0.91 | 0.78 | 0.85 | 0.68 | 1.00 | 0.79 |
| `layered` | 0.43 | 0.92 | 1.00 | 0.51 | 0.00 | 0.98 | 0.95 | 0.38 | 0.65 | 0.92 | 0.90 | 0.90 | 0.43 |
| `gliner_pii` | 0.00 | 0.92 | 0.05 | 0.64 | 0.25 | 0.86 | 0.82 | 0.29 | 0.89 | 0.61 | 0.37 | 0.70 | 0.14 |
| `privacy_filter` | 0.43 | 0.08 | 0.00 | 0.00 | 1.00 | 0.98 | 0.00 | 0.00 | 0.64 | 0.54 | 0.00 | 0.50 | 0.50 |
| `gcp_dlp` | 0.00 | 0.92 | 0.00 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.56 | 0.46 | 0.00 | 1.00 | 0.21 |
| `presidio` | 0.29 | 0.00 | 0.00 | 0.00 | 1.00 | 0.96 | 0.00 | 0.00 | 0.51 | 1.00 | 0.00 | 1.00 | 0.00 |
| `regex` | 0.00 | 0.83 | 0.85 | 0.00 | 0.00 | 0.96 | 0.95 | 0.38 | 0.00 | 0.92 | 0.90 | 0.90 | 0.29 |

## Deployment cost

Zero-leak alone is half the picture — what does each model cost to *run*?
The table below gives the **artifact size** (what you download or
include in a Docker image), the **peak RSS** during inference, and the
**p50 latency per redaction**.

| Adapter | Local? | Model size | Peak RSS | p50 | p95 |
|---|:---:|---:|---:|---:|---:|
| `regex` | ✅ | < 1 MB | ~ 30 MB | < 1 ms | < 1 ms |
| `presidio` | ✅ | ~ 200 MB | ~ 400 MB¹ | 6 ms | 8 ms |
| `v45_phase3` ⭐ | ✅ | **278 MB** (INT8 ONNX) | **1.1 GB** (Rust `ort` runtime, CPU) | **9 ms** | **22 ms** |
| `gliner_pii` | ✅ | ~ 500 MB¹ | ~ 1.5 GB¹ | 104 ms | 112 ms |
| `opf_rs` | ✅ | ~ 1.4 GB¹ | ~ 6 GB¹ | < 1 ms² | < 1 ms² |
| `privacy_filter_ft_v2` | ✅ | ~ 1.4 GB¹ | ~ 6 GB¹ | 23 ms | 24 ms |
| `privacy_filter_ft_v3` | ✅ | ~ 1.4 GB¹ | ~ 6 GB¹ | 118 ms | 237 ms |
| `privacy_filter` (base OPF) | ✅ | ~ 1.4 GB¹ | ~ 6 GB¹ | 22 ms | 23 ms |
| `gcp_dlp` | ❌ cloud | 0 MB local | 0 MB local | 84 ms | 185 ms |
| `claude` (claude-opus-4-7) | ❌ cloud | 0 MB local | 0 MB local | 1 550 ms | 2 879 ms |
| `gpt5` (gpt-5.5) | ❌ cloud | 0 MB local | 0 MB local | 2 173 ms | 4 722 ms |
| `gemini` (gemini-3.1-pro-preview) | ❌ cloud | 0 MB local | 0 MB local | 3 754 ms | 8 237 ms |

`v45_phase3` is the only adapter that is **simultaneously** within 5
points of frontier zero-leak on the framework-coverage tables, under
300 MB on disk, and under 10 ms per redaction — fits in every laptop
screenpipe targets. The 1.4 B `privacy_filter` / `opf_rs` family runs
but needs ~6 GB resident, which knocks every laptop with 8 GB total
RAM into swap. The cloud-API adapters trade local memory for cents
per call and 1.5–8 seconds of latency per redaction.

The `v45_phase3` row's Peak RSS comes from a real `/usr/bin/time -l`
measurement of the [`v45_phase3_smoke`](https://github.com/screenpipe/screenpipe/blob/main/crates/screenpipe-redact/examples/v45_phase3_smoke.rs)
example in the `screenpipe-redact` crate (`cargo run --release
--example v45_phase3_smoke --features onnx-cpu`). 278 MB of that is
the model on disk; the remaining ~ 830 MB is ONNX Runtime's working
memory + embedding tables + tokenizer.

¹ "~" values are documented from model card / well-known sizes, not
re-measured this run. Re-measurement of every adapter is on the
post-v0.1 roadmap.

² `opf_rs`'s ~ 0 ms p50 is artefact of warm-up batching from the
underlying Rust runtime; per-call latency on a long-running daemon is
~ 5 ms.

_Bench size: 345 gold-bearing cases, 77 negatives. `v45_phase3` scored on the 47-case `sample.jsonl` public sub-bench (now includes PHI / PCI / intl_id / Art. 9 / multilingual-name shards as tasters of the full private-bench coverage) — wider CI than the full set. Load-bearing claim is the 735-case private bench, where the same INT8-ONNX model lands at 85.5–87.2% zero-leak across every compliance framework (see [framework_coverage.md](framework_coverage.md)). [METHODOLOGY.md](../METHODOLOGY.md) for scoring details, [LIMITATIONS.md](../LIMITATIONS.md) for caveats._
