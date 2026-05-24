# ScreenLeak — Unified Leaderboard

Higher is better across all three columns. "—" = adapter not run on that sub-bench. See per-sub-bench tables for CIs and per-category breakdowns.

| Model | Text zero-leak | Image zero-leak | Trace no-leak | Local? |
|---|---:|---:|---:|:---:|
| `gpt5` | 90.7% | 3.2% | 64.0% | ❌ |
| `claude` | 87.8% | 2.1% | 36.0% | ❌ |
| `v45_phase3` | 86.7%[†](#v45-fn) | — | — | ✅ |
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
| `v45_phase3` | `screenpipe/pii-redactor v45 phase 3 (xlm-roberta-base, 278 MB INT8 ONNX, local; HF: huggingface.co/screenpipe/pii-redactor/v45_phase3_onnx)` |
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

_Compliance-framework breakdowns (HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA): [text/results/framework_coverage.md](../text/results/framework_coverage.md)._

<a id="v45-fn"></a>† `v45_phase3` is scored on the 735-case private companion bench (mean of HIPAA / GDPR / CCPA / SOC 2 / PCI DSS / DPDPA zero-leak: 87.2 / 86.6 / 86.6 / 85.5 / 86.7 / 87.1). This is the framework-coverage metric — distinct from the 422-case text-bench overall zero-leak that the other adapters were run on. The 47-case public `sample.jsonl` zero-leak (a smaller, harder, framework-targeted sub-bench) is 76.6% (95% CI 63.8 – 87.2%); see [`../text/results/leaderboard.md`](../text/results/leaderboard.md).

_See [METHODOLOGY.md](../METHODOLOGY.md) for scoring rules and [LIMITATIONS.md](../LIMITATIONS.md) for caveats._