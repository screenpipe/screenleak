# Framework coverage — text / image / trace

One label-subset dict ([`scoring/frameworks.py`](../scoring/frameworks.py)), three sub-benches, one compliance picture per adapter. Cases with no in-scope spans are excluded from a framework's denominator. Mapping mirrors GCP DLP's `FRAMEWORK_INFO_TYPES`.

## Load-bearing — verified on the private val sets

`screenleak-public` ships the probes; the **private companion** runs them against the full corpus. These are the numbers customers and auditors should reference.

### Headline — v45_phase3 (text) · rfdetr (image) · gpt5 (trace)

| Framework | Text (v45_phase3) | Image (rfdetr) | Trace (gpt5) | Composite\* |
|---|---:|---:|---:|---:|
| HIPAA   | 91.8% | 95.8% | 76.0% | **87.9%** |
| GDPR    | 90.2% | 95.2% | 68.0% | 84.5% |
| CCPA    | 90.2% | 95.2% | 68.0% | 84.5% |
| SOC 2   | 88.0% | 95.7% | 68.0% | 83.9% |
| PCI DSS | 88.7% | 96.8% | 78.3% | 87.9% |
| DPDPA   | 91.6% | 95.8% | 72.0% | 86.5% |

\* Geometric mean across the three surfaces. Captures the *chain*: every surface where PII could leak is evaluated, and the weakest link sets the system's overall compliance posture.

### Text — 422-case private bench

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| **`v45_phase3`** ⭐ local (278 MB INT8 ONNX) | **91.8%** | **90.2%** | **90.2%** | **88.0%** | **88.7%** | **91.6%** |
| `gcp_dlp` (cloud API) | 68.0% | 53.3% | 53.3% | 61.0% | 56.0% | 64.3% |
| `regex` (deterministic) | 34.6% | 34.3% | 34.3% | 34.9% | 8.9% | 39.4% |

Denominators (in-scope applicable cases): HIPAA 231 · GDPR 306 · CCPA 306 · SOC 2 241 · PCI DSS 168 · DPDPA 249.

### Image — 221-image private val (IoU ≥ 0.30)

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| **`rfdetr`** ⭐ local (108 MB ONNX) | **95.8%** | **95.2%** | **95.2%** | **95.7%** | **96.8%** | **95.8%** |

Denominators: HIPAA 168 · GDPR 168 · CCPA 168 · SOC 2 186 · PCI DSS 186 · DPDPA 168.

Frontier vision APIs and deterministic baselines all sit at ≲ 5 % on the overall image bench (see [`image/results/leaderboard.md`](../image/results/leaderboard.md)); per-framework numbers stay in that band.

### Trace — 25-trace private val

| Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---:|---:|---:|---:|---:|---:|
| **`gpt5`** (gpt-5.5) | **76.0%** | **68.0%** | **68.0%** | **68.0%** | **78.3%** | **72.0%** |
| `gemini` (gemini-3.1-pro-preview) | 56.0% | 36.0% | 36.0% | 36.0% | 56.5% | 52.0% |
| `claude` (claude-opus-4-7) | 52.0% | 44.0% | 44.0% | 44.0% | 52.2% | 48.0% |

Denominators: HIPAA 25 · GDPR 25 · CCPA 25 · SOC 2 25 · PCI DSS 23 · DPDPA 25.

## Verifiable from this repo — public sample

Smaller numbers, smaller corpus, same probes. Lets anyone confirm the scoring kernel runs without access to the private corpus:

| Surface | Adapter | HIPAA | GDPR | CCPA | SOC 2 | PCI DSS | DPDPA |
|---|---|---:|---:|---:|---:|---:|---:|
| text (51 cases) | `v45_phase3` | 81.2% | 85.4% | 85.4% | 80.0% | 69.6% | 82.9% |
| text (51 cases) | `gcp_dlp` | 43.8% | 36.6% | 36.6% | 37.1% | 30.4% | 42.9% |
| text (51 cases) | `regex` | 37.5% | 41.5% | 41.5% | 40.0% | 13.0% | 42.9% |
| image (30 imgs) | `rfdetr` | 100.0% | 95.8% | 95.8% | 100.0% | 100.0% | 100.0% |
| trace | _replays not public_ | — | — | — | — | — | — |

## Run it yourself

```bash
python text/src/framework_coverage.py  --adapter v45_phase3 gcp_dlp regex
RFDETR_MODEL_PATH=~/.screenpipe/models/rfdetr_v8.onnx \
  python image/src/framework_coverage.py --adapter rfdetr
# trace requires replay JSONLs — produced by trace/src/replay.py in the private companion
python trace/src/framework_coverage.py \
  --traces trace/data/injected_sample.jsonl \
  --replays trace/results/replays/*.jsonl
```

Each probe writes `framework_coverage_sample.md` next to its sub-bench leaderboard. The shared dict is in [`scoring/frameworks.py`](../scoring/frameworks.py).

## Moat

- **Public**: 13 canonical labels, framework → label-subset mapping, probe scripts, small per-surface sample.
- **Private**: 422-case text bench + adversarial / multilingual / Art. 9 / sensitive-negative shards (`screenpipe-pii-bench`), image generator + 2 206-image corpus (`screenpipe-pii-bench-image`), trace generator + 50-trace corpus + replay infrastructure, model weights, training mixtures.

The compliance-coverage *claim* is verifiable from the public sample. The *load-bearing numbers* require the corpus. Researchers with a legitimate use case can request access at `louis@screenpi.pe`.

_See [`METHODOLOGY.md`](../METHODOLOGY.md), [`THREAT_MODEL.md`](../THREAT_MODEL.md), [`LIMITATIONS.md`](../LIMITATIONS.md)._
