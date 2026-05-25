# Framework coverage — text / image / trace, unified

For each compliance framework (HIPAA / GDPR / CCPA / SOC 2 / PCI DSS /
DPDPA), every adapter is scored against the subset of bench labels
that framework cares about. The label-subset mapping is the **same
dict** across all three sub-benches — defined once in
[`scoring/frameworks.py`](../scoring/frameworks.py) and imported by
each surface's `framework_coverage.py` probe. Cases with no in-scope
spans are excluded from a framework's denominator.

> Label-subset mapping mirrors Google Cloud DLP's `FRAMEWORK_INFO_TYPES`
> convention. See [`CATEGORIES.md`](../CATEGORIES.md) for the 13
> canonical labels and [`scoring/frameworks.py`](../scoring/frameworks.py)
> for the exact framework → label-subset definitions.

## Text bench

`v45_phase3` on the 735-case private companion bench
([`screenpipe-pii-bench`](https://github.com/screenpipe/screenpipe-pii-bench)):

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| **`v45_phase3`** ⭐ local (INT8 ONNX, 278 MB) | **87.2%** | **86.6%** | **86.6%** | **85.5%** | **86.7%** | **87.1%** |
| `gcp_dlp` (cloud API) | 69.5% | 63.5% | 63.5% | 59.0% | 60.7% | 66.8% |
| `regex` (deterministic) | 20.6% | 23.1% | 23.1% | 22.0% | 5.5% | 25.2% |

On the 51-case public sample (PHI / PCI / intl-ID / Art. 9 / multilingual
tasters):

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| `gemini` (gemini-3.1-pro) | 90.6% | **92.7%** | **92.7%** | 88.6% | 82.6% | 91.4% |
| `claude` (claude-opus-4-7) | 90.6% | 90.2% | 90.2% | **91.4%** | **87.0%** | 91.4% |
| **`v45_phase3`** ⭐ local | 81.2% | 85.4% | 85.4% | 80.0% | 69.6% | 82.9% |
| `gcp_dlp` | 43.8% | 36.6% | 36.6% | 37.1% | 30.4% | 42.9% |
| `regex` | 37.5% | 41.5% | 41.5% | 40.0% | 13.0% | 42.9% |

See [`text/results/framework_coverage.md`](../text/results/framework_coverage.md)
for caveats, denominators, and the structural notes (Claude
oversmashes 25% of negatives on the sample; cloud APIs take 1.5–3.6 s
per call).

## Image bench

On the 30-image public sample (`image/corpus/sample/`, IoU ≥ 0.30):

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| **`rfdetr`** ⭐ local (RF-DETR-Nano, 108 MB ONNX) | **100.0%** | **95.8%** | **95.8%** | **100.0%** | **100.0%** | **100.0%** |
| Frontier vision APIs (gemini / gpt5 / claude) | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% |
| `gcp_dlp` | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% |
| `regex_ocr` (Tesseract + 16 regex) | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% | ≲ 5% |

The "≲ 5%" bound comes from the existing image-bench leaderboard's
overall per-image zero-leak (`gemini` 4.2%, `gpt5` 3.2%, `claude`
2.1%, `gcp_dlp` 2.6%, `regex_ocr` 2.6%, `presidio_image` 0.5%) —
per-framework numbers can't exceed the overall, and on this sample the
frontier vision adapters' framework numbers cluster in the 1–5% band.
A full per-adapter run is on the v0.1 roadmap and tracked in
[`LIMITATIONS.md`](../LIMITATIONS.md). See
[`image/results/leaderboard.md`](../image/results/leaderboard.md) for
the verified overall numbers and 95% CIs.

**Two structural caveats on the image bench:**

- The image-bench corpus does not yet contain gold spans for
  `private_handle`, `private_id`, or `private_date`. HIPAA / SOC 2 /
  PCI / DPDPA all include `private_id` and `private_date` in scope, so
  the per-image-framework denominators are smaller than they could
  be — backporting those three categories is a v0.1 item.
- The model's val split is image-disjoint but distribution-matched
  with its training set. The 95–100% per-framework numbers are what's
  reachable when you can train on the synthetic-screen generator, not
  a claim about arbitrary real Slack/Outlook screenshots.

## Trace bench

The trace bench scores **leakage when an agent observes injected PII
and is asked to summarize**. The headline numbers (overall no-leak
rate on n=25 traces) live in
[`trace/results/leaderboard.md`](../trace/results/leaderboard.md):

| Adapter | Overall no-leak | Mean leaks/trace |
|---|---:|---:|
| `gpt5` (gpt-5.5) | 64.0% (95% CI 44.0 – 80.0%) | 0.64 |
| `claude` (claude-opus-4-7) | 36.0% (16.0 – 56.0%) | 1.12 |
| `gemini` (gemini-3.1-pro-preview) | 20.0% (4.0 – 36.0%) | 1.28 |

Per-framework no-leak requires the per-trace replay outputs to be
re-scored against framework-filtered injected_pii sets. The
[`trace/src/framework_coverage.py`](../trace/src/framework_coverage.py)
probe is in place; running it against replays + publishing
per-framework numbers is the next step (replay JSONLs aren't in the
public repo). Per-category leak rates from `trace/results/leaderboard.md`
suggest the rough shape — frontier models leak `private_company` and
`private_person` ~ 50 – 100% of the time across all frameworks that
cover those labels.

## How to run

Each sub-bench has its own probe; all import the shared dict from
[`scoring/frameworks.py`](../scoring/frameworks.py):

```bash
# Text bench
python text/src/framework_coverage.py --adapter v45_phase3 gcp_dlp regex

# Image bench (needs RFDETR_MODEL_PATH for the local model)
RFDETR_MODEL_PATH=~/.screenpipe/models/rfdetr_v8.onnx \
  python image/src/framework_coverage.py --adapter rfdetr

# Trace bench (needs replay files — produced by trace/src/replay.py first)
python trace/src/framework_coverage.py \
  --traces trace/data/injected_sample.jsonl \
  --replays trace/results/replays/*.jsonl
```

Each writes a `framework_coverage_sample.md` next to its sub-bench
leaderboard. This top-level page bundles the three together as the
single cross-surface compliance-coverage view.

## What's public vs private

**Public** (everything you can reproduce from this repo):
- The 13 canonical labels ([`CATEGORIES.md`](../CATEGORIES.md))
- The framework → label-subset mapping
  ([`scoring/frameworks.py`](../scoring/frameworks.py))
- The per-surface probe scripts
- A small public sample per surface (51-case text, 30-image, 5-trace)
- The headline private-bench numbers in this page

**Private** (the moat — kept in the companion repos):
- 422-case text private bench + `intl_id`, `special_category`,
  `multilingual_names`, `sensitive_negative`, `intl_id_adversarial`
  shards
- The image generator (HTML/CSS templates, headless-Chromium DOM-bbox
  extraction, the 905-image augmented corpus)
- The trace generator (`gen_specs.py`, `pii_pool.py`, `inject.py`)
- Seeds, model weights, training mixtures

The taxonomy and the probe scripts being public doesn't help a
competitor catch up — they still need to build the corpus, which is
the months of work. The framework_coverage interface is the
compliance-facing API; the corpus is the moat behind it.

_See [`METHODOLOGY.md`](../METHODOLOGY.md) for scoring rules,
[`THREAT_MODEL.md`](../THREAT_MODEL.md) for what counts as a leak, and
[`LIMITATIONS.md`](../LIMITATIONS.md) for caveats._
