# Image-PII Bench — Leaderboard

Sorted by **per-image zero-leak** at IoU ≥ 0.3. Zero-leak = fraction of PII-bearing images where the redactor caught EVERY gold region (with a label that maps to the gold's).

| Adapter | Zero-leak | Oversmash | Macro-F1 | Micro-F1 | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| `rfdetr` | 95.3% | 0.0% | 0.871 | 0.970 | 285 | 432 |
| `gemini` | 4.2% | 9.7% | 0.038 | 0.034 | 6988 | 19836 |
| `gpt5` | 3.2% | 22.6% | 0.093 | 0.136 | 39534 | 45623 |
| `regex_ocr` | 2.6% | 3.2% | 0.318 | 0.400 | 369 | 547 |
| `gcp_dlp` | 2.6% | 19.4% | 0.218 | 0.343 | 413 | 612 |
| `claude` | 2.1% | 35.5% | 0.100 | 0.153 | 7417 | 11469 |
| `presidio_image` | 0.5% | 48.4% | 0.190 | 0.269 | 377 | 548 |

## Per-category recall

| Adapter | private_address | private_channel | private_company | private_date | private_email | private_handle | private_id | private_person | private_phone | private_repo | private_url | secret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rfdetr` | 1.00 | 1.00 | 0.99 | 0.00 | 0.99 | 0.00 | 0.00 | 0.98 | 0.97 | 1.00 | 1.00 | 0.99 |
| `gemini` | 0.08 | 0.00 | 0.08 | 0.00 | 0.04 | 0.00 | 0.00 | 0.03 | 0.14 | 0.02 | 0.02 | 0.02 |
| `gpt5` | 0.00 | 0.08 | 0.11 | 0.00 | 0.15 | 0.00 | 0.00 | 0.10 | 0.17 | 0.00 | 0.05 | 0.02 |
| `regex_ocr` | 0.00 | 0.00 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | 0.00 | 0.92 | 0.00 | 0.24 | 0.51 |
| `gcp_dlp` | 0.17 | 0.00 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.63 | 0.31 | 0.00 | 0.89 | 0.11 |
| `claude` | 0.00 | 0.00 | 0.43 | 0.00 | 0.14 | 0.00 | 0.00 | 0.15 | 0.17 | 0.12 | 0.09 | 0.37 |
| `presidio_image` | 0.00 | 0.00 | 0.00 | 0.00 | 0.88 | 0.00 | 0.00 | 0.33 | 0.75 | 0.00 | 0.79 | 0.00 |

## Per-template zero-leak

| Adapter | arc_tabs | calendar_event | confluence_page | cursor_workspace | github_pr | onepassword_vault | outlook_inbox | slack_channel | terminal_session |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rfdetr` | 1.00 | 0.62 | 1.00 | 0.94 | 1.00 | 1.00 | 0.97 | 0.97 | 1.00 |
| `gemini` | 0.00 | 0.06 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 |
| `gpt5` | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `regex_ocr` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 |
| `gcp_dlp` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 |
| `claude` | 0.00 | 0.06 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 |
| `presidio_image` | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 |

_Bench size: 190 PII-bearing images, 31 negatives. IoU threshold = 0.3._
