# Trace-PII Leaderboard

Sorted by **no-leak rate** (% of traces where the model emitted zero injected PII). 95% bootstrap CI in brackets.

| Adapter | No-leak (95% CI) | Mean leaks/trace | n | errors | p50 (ms) | p95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| `gpt5` | 64.0% (44.0%-80.0%) | 0.64 | 25 | 0 | 4538 | 14480 |
| `claude` | 36.0% (16.0%-56.0%) | 1.12 | 25 | 0 | 6467 | 16374 |
| `gemini` | 20.0% (4.0%-36.0%) | 1.28 | 25 | 0 | 6583 | 11114 |

## Per-category leak rate

| Adapter | private_address | private_channel | private_company | private_date | private_email | private_handle | private_id | private_person | private_phone | private_repo | private_url | secret |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt5` | 7.7% | 8.3% | 50.0% | 0.0% | 10.0% | 42.9% | 33.3% | 50.0% | 0.0% | 42.9% | 0.0% | 0.0% |
| `claude` | 0.0% | 41.7% | 100.0% | 38.5% | 10.0% | 28.6% | 33.3% | 83.3% | 14.3% | 42.9% | 0.0% | 11.1% |
| `gemini` | 7.7% | 50.0% | 100.0% | 0.0% | 10.0% | 28.6% | 66.7% | 83.3% | 14.3% | 100.0% | 0.0% | 11.1% |

_See METHODOLOGY.md for scoring definitions and THREAT_MODEL.md for what counts as a leak._