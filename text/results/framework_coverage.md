# Per-framework zero-leak

Compliance frameworks score each adapter against the subset of PII
labels that framework cares about. Cases with no in-scope labels are
excluded from the denominator (you can't leak what isn't there).

Label-subset mapping mirrors Google Cloud DLP's `FRAMEWORK_INFO_TYPES`
convention, collapsed onto the bench's canonical label space. See
[`text/src/framework_coverage.py`](../src/framework_coverage.py) for
the exact `FRAMEWORK_LABELS` dict.

## On the 51-case public sample (`sample.jsonl`)

The public sample includes light tasters of the harder shards in the
private bench: PHI cases (HIPAA-relevant patient/MRN/DOB combos), PCI
cases (card last-fours, transaction IDs, full card numbers), three
international ID formats (UK NINO, Indian Aadhaar, Brazil CPF), two
multilingual person names (Korean, Arabic), two GDPR Art. 9 cases
(religion + sexual orientation), and one sensitive-negative trap
(public AIDS Day mention).

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| `gemini` (gemini-3.1-pro-preview) | 90.6% | **92.7%** | **92.7%** | 88.6% | 82.6% | 91.4% |
| `claude` (claude-opus-4-7) | 90.6% | 90.2% | 90.2% | **91.4%** | **87.0%** | 91.4% |
| `v45_phase3` ⭐ local (278 MB, 9 ms) | 81.2% | 85.4% | 85.4% | 80.0% | 69.6% | 82.9% |
| `gcp_dlp` | 43.8% | 36.6% | 36.6% | 37.1% | 30.4% | 42.9% |
| `regex` | 37.5% | 41.5% | 41.5% | 40.0% | 13.0% | 42.9% |

Frontier APIs (`gemini`, `claude`) lead by 5–15 points on most
frameworks; `v45_phase3` is within striking distance at 1/100th the
latency and zero per-call cost. The local model leads `gcp_dlp` by
30–47 points across every framework and `regex` by 28–57 points. The
public sample is small (N = 23–41 per framework after filtering for
in-scope cases), so CIs are wide; the load-bearing claim is the 735-
case private bench below.

Two structural caveats on the frontier numbers:

- **Oversmash matters.** `claude` redacts 25% of negative cases (the
  "settings" / "World AIDS Day" traps), `v45_phase3` redacts 0%. The
  framework_coverage rate only measures missed-PII, not over-redaction
  — see `leaderboard.md` for oversmash columns.
- **Cost.** Cloud-API calls run $0.001–$0.01 per redaction at
  frontier-model rates and 1.7 s p50. `v45_phase3` is 9 ms p50,
  zero per-call, and runs in offline / air-gapped environments.

Per-framework denominators on this sample:

| | applicable cases |
|---|---:|
| HIPAA | 32 |
| GDPR / CCPA | 41 |
| SOC 2 | 35 |
| PCI DSS | 23 |
| DPDPA | 35 |

### Overall zero-leak (all-labels-in-scope) on the same 51-case sample

| Adapter | Zero-leak | Oversmash | p50 |
|---|---:|---:|---:|
| `gemini` (gemini-3.1-pro-preview) | **89.4%** (95% CI 80.9 – 97.9%) | **0.0%** | 3 600 ms |
| `claude` (claude-opus-4-7) | 87.2% (95% CI 76.6 – 95.7%) | 25.0% | 1 719 ms |
| `v45_phase3` ⭐ local | 76.6% (95% CI 63.8 – 87.2%) | **0.0%** | **9 ms** |

Three takeaways:

1. **Gemini wins the public sample** — top zero-leak *and* zero
   oversmash. Worth the 3.6 s p50 if the workload is occasional.
2. **Claude over-redacts a quarter of negatives** — the 25% oversmash
   is one of four negatives ("The Real Estate Team OS - Follow Up
   Boss", which Claude labels as `private_company`; the bench's
   `private_company` excludes vendor / product brand names). Claude
   *does* hold the "World AIDS Day" sensitive-negative trap — that
   case it gets right.
3. **v45_phase3 is the only model that's both zero-oversmash and
   sub-10-ms** — 400x faster than Claude / Gemini, free per call,
   runs offline. Costs ~9 points of zero-leak vs Gemini.

The `gpt5` (GPT-5.5) adapter is omitted from this section because the
`OPENAI_API_KEY` wasn't available in this run. Its historical
422-case private-bench score is in [`leaderboard.md`](leaderboard.md).

## On the 735-case private bench (screenpipe-pii-bench)

Reference numbers from the full private corpus — much larger N,
includes the `intl_id` shard (24 country IDs), `special_category`
shard (34 GDPR Art. 9 cases), `multilingual_names` shard (30 non-Latin
person names), and `sensitive_negative` shard (15 looks-sensitive-but-
isn't cases). Reproducible from `screenpipe-pii-bench` →
`results/probes/framework_coverage_probe.json`.

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| `v45_phase3` (INT8 ONNX, 278 MB) | **87.2%** | **86.6%** | **86.6%** | **85.5%** | **86.7%** | **87.1%** |
| `v45_phase3` (fp32 ONNX) | 87.0% | 86.6% | 86.6% | 85.1% | 86.4% | 86.8% |
| `gcp_dlp` (cloud API, ~$1/1000 chars) | 69.5% | 63.5% | 63.5% | 59.0% | 60.7% | 66.8% |
| `regex` (deterministic baseline) | 20.6% | 23.1% | 23.1% | 22.0% | 5.5% | 25.2% |

INT8 quantization is essentially free in accuracy (within noise of
fp32) while cutting the model from 1.1 GB to 278 MB and CPU latency
from ~30 ms to ~9 ms p50.

## How to read these tables

A framework's zero-leak rate is the fraction of *applicable* cases
where every in-scope gold span was caught. For `v45_phase3` (INT8
ONNX) on the private 735-case bench:

- **HIPAA 87.2%** = 369 of 423 cases with HIPAA-relevant PII had
  all those spans redacted. The 54 leaks are dominated by
  multilingual-name shards + a few hard adversarial ID surfaces.
- **PCI DSS 86.7%** = on 383 cases containing PCI-relevant data
  (person / id / date / secret), 332 had every span caught.
- **Lead over `gcp_dlp`**: 17.7 (HIPAA) to 26.5 (SOC 2) points
  across every framework. Lead over `regex`: 62 to 81 points.
- **`sensitive_negative` shard** (15 cases that *look* like Art. 9
  but contain no PII): `v45_phase3` returns 0 false positives — the
  bench's oversmash trap is held.

## What's missing

- The public sample includes a light taster of each hard shard
  (4 PHI cases, 3 PCI, 3 intl IDs, 2 multilingual names, 2 Art. 9,
  1 sensitive-negative). The full shards live in the private companion
  bench:
  - `intl_id` (24 country IDs)
  - `special_category` (34 GDPR Art. 9 cases)
  - `multilingual_names` (30 non-Latin person names)
  - `sensitive_negative` (15 looks-sensitive-but-isn't cases)
  - `intl_id_adversarial` (20 adversarial perturbations of intl IDs)
- The public sample is intentionally small (N ≈ 23–41 cases per
  framework after filtering) — wide CIs. Use the private-bench numbers
  for ranking.
- `v45_phase3` has clear public-sample headroom on PHI-specific date
  formats ("DOB 1985-03-14", "appt 2026-04-12") and a handful of
  short-token IDs ("*4242", "MRN-7430182"). These are addressed in
  v46 (in training).

_See [`leaderboard.md`](leaderboard.md) for overall zero-leak and
[`../METHODOLOGY.md`](../METHODOLOGY.md) for scoring rules._
