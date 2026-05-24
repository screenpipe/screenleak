# Per-framework zero-leak

Compliance frameworks score each adapter against the subset of PII
labels that framework cares about. Cases with no in-scope labels are
excluded from the denominator (you can't leak what isn't there).

Label-subset mapping mirrors Google Cloud DLP's `FRAMEWORK_INFO_TYPES`
convention, collapsed onto the bench's canonical label space. See
[`text/src/framework_coverage.py`](../src/framework_coverage.py) for
the exact `FRAMEWORK_LABELS` dict.

## On the 36-case public sample (`sample.jsonl`)

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| `v45_phase3` ⭐ local | **100.0%** | **100.0%** | **100.0%** | **95.2%** | **90.0%** | **100.0%** |
| `regex` | 66.7% | 63.0% | 63.0% | 66.7% | 30.0% | 71.4% |
| `gcp_dlp` | 66.7% | 48.1% | 48.1% | 52.4% | 40.0% | 61.9% |

Per-framework denominators on this sample:

| | applicable cases |
|---|---:|
| HIPAA | 18 |
| GDPR / CCPA | 27 |
| SOC 2 | 21 |
| PCI DSS | 10 |
| DPDPA | 21 |

## On the 643-case private bench (screenpipe-pii-bench)

Reference numbers from the full private corpus — much larger N,
includes the `intl_id` shard (24 country IDs), `special_category`
shard (34 GDPR Art. 9 cases), `multilingual_names` shard (30 non-Latin
person names), and `sensitive_negative` shard (15 looks-sensitive-but-
isn't cases). Reproducible from `screenpipe-pii-bench` →
`results/probes/framework_coverage_probe.json`.

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| `v45_phase3` (INT8 ONNX, 278 MB) | 90.2% | 89.3% | 89.3% | 87.4% | 89.2% | 90.2% |
| `v45_phase3` (fp32 PyTorch) | 88.6% | 88.2% | 88.2% | 85.8% | 87.7% | 88.7% |
| `gliner2_pii_v45` (schema-driven, 0.3 B) | 86.9% | 84.4% | 84.4% | 86.8% | 87.9% | 86.3% |
| `v43_student` (320 KB MLP + 22-rule cascade) | 75.5% | 77.4% | 77.4% | 77.9% | 81.0% | 76.8% |
| `gcp_dlp` (cloud API, ~$1/1000 chars) | 69.5% | 63.5% | 63.5% | 59.0% | 60.7% | 66.8% |
| `regex` (deterministic baseline) | 22.6% | 24.0% | 24.0% | 24.5% | 6.0% | 26.5% |

## How to read these tables

A framework's zero-leak rate is the fraction of *applicable* cases
where every in-scope gold span was caught. For `v45_phase3` on the
private 643-case bench:

- **HIPAA 90.2%** = 349 of 387 cases with HIPAA-relevant PII had
  all those spans redacted. The 38 leaks are dominated by
  multilingual names + a few hard adversarial ID surfaces.
- **PCI DSS 89.2%** = on 351 cases containing PCI-relevant data
  (person / id / date / secret), 313 had every span caught.
- **`sensitive_negative` shard** (15 cases that *look* like Art. 9
  but contain no PII): `v45_phase3` returns 0 false positives. The
  bench's main public oversmash claim is "Art. 9-relevant adapters
  don't over-redact public-topic mentions of HIV / depression /
  religion / etc."

## What's missing

- **`private_sensitive`** (Art. 9 / non-Safe-Harbor PHI) doesn't yet
  appear in the public 36-case sample. The full private bench has 34
  cases of it; `v45_phase3` scores 88% catch on those (vs 6% for
  predecessor models). The public sample will be expanded with
  sensitive-context cases in a future release of ScreenLeak.
- The public sample is small enough that the 100% scores have wide CIs
  — use the private-bench numbers as the load-bearing claim.

_See [`leaderboard.md`](leaderboard.md) for overall zero-leak and
[`../METHODOLOGY.md`](../METHODOLOGY.md) for scoring rules._
