# ScreenLeak — Unified Leaderboard

Higher is better across all three columns. "—" = adapter not run on that sub-bench. See per-sub-bench tables for CIs and per-category breakdowns.

| Model | Text zero-leak | Image zero-leak | Trace no-leak | Local? |
|---|---:|---:|---:|:---:|
| `gpt5` | 90.7% | 3.2% | 64.0% | ❌ |
| `claude` | 87.8% | 2.1% | 36.0% | ❌ |
| `gemini` | 91.0% | 4.2% | 20.0% | ❌ |
| `rfdetr` | — | 95.3% | — | ✅ |
| `gcp_dlp` | 37.7% | 2.6% | — | ❌ |
| `regex_ocr` | — | 2.6% | — | ✅ |
| `presidio_image` | — | 0.5% | — | ✅ |
| `privacy_filter_ft_v6` | 80.9% | — | — | ❌ |
| `privacy_filter_ft_v3` | 79.4% | — | — | ✅ |
| `privacy_filter_ft_v2` | 78.0% | — | — | ✅ |
| `opf_rs` | 75.9% | — | — | ✅ |
| `layered` | 65.8% | — | — | ❌ |
| `gliner_pii` | 62.6% | — | — | ✅ |
| `privacy_filter` | 38.6% | — | — | ✅ |
| `presidio` | 35.4% | — | — | ✅ |
| `regex` | 33.9% | — | — | ✅ |

## Adapter → model

| Adapter | Model id |
|---|---|
| `gpt5` | `gpt-5.5` |
| `claude` | `claude-opus-4-7` |
| `gemini` | `gemini-3.1-pro-preview` |
| `rfdetr` | `screenpipe/rfdetr_v8 (DINOv2-S + LWDETR, 12-class, local fine-tune)` |
| `gcp_dlp` | `Google Cloud DLP / Sensitive Data Protection (cloud API)` |
| `regex_ocr` | `Tesseract OCR + 16 regex (deterministic baseline)` |
| `presidio_image` | `microsoft/presidio-image-redactor` |
| `privacy_filter_ft_v6` | `_unmapped — see adapter source_` |
| `privacy_filter_ft_v3` | `screenpipe/pii-redactor v3 (fine-tune)` |
| `privacy_filter_ft_v2` | `screenpipe/pii-redactor v2 (fine-tune)` |
| `opf_rs` | `screenpipe/pii-redactor (1.4B MoE NER, fine-tune)` |
| `layered` | `(stacked baseline)` |
| `gliner_pii` | `urchade/gliner_multi_pii-v1` |
| `privacy_filter` | `openai/privacy-filter (1.5B / 50M-active, base)` |
| `presidio` | `microsoft/presidio-analyzer` |
| `regex` | `(deterministic baseline, no model)` |

_Per-sub-bench leaderboards: [text](../text/results/leaderboard.md), [image](../image/results/leaderboard.md), [trace](../trace/results/leaderboard.md)._

_See [METHODOLOGY.md](../METHODOLOGY.md) for scoring rules and [LIMITATIONS.md](../LIMITATIONS.md) for caveats._