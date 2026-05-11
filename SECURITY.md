# Security policy

## Supported versions

ScreenLeak is research infrastructure, not production software. We provide best-effort fixes for the latest tagged release; older versions are not maintained.

## Reporting a vulnerability

**Please do not file a public GitHub issue for security concerns.**

Email **`louis@screenpi.pe`** with:

- A description of the issue
- Reproduction steps
- The impact you believe it has
- Any suggested fix

We aim to acknowledge within 72 hours and provide an initial assessment within 7 days.

## What's in scope

- Real PII accidentally checked into the corpus (i.e. data that wasn't synthetic)
- Real API keys / credentials checked into source
- Code that exfiltrates user data when running the bench
- Vulnerabilities in vendor scripts that could overwrite or destroy user files

## What's out of scope

- Adversarial inputs that fool a specific model on the bench (that's a model issue, not a bench issue — file as a regular issue or write a paper)
- Performance regressions
- Issues in the upstream models we benchmark
- Issues in API SDKs (anthropic, openai, google-genai) — report to those vendors

## Synthetic-data invariant

All PII in `text/data/`, `image/corpus/`, and `trace/data/` is **synthetic**. If you find a real-looking item in the corpus that you believe is genuinely identifying, email immediately and we will quarantine and rotate.

Tools to verify yourself:

```bash
make pre-oss     # runs scripts/pre_oss_check.sh
```

This checks for hardcoded local paths, real-looking secrets (real OpenAI/Anthropic/AWS key prefixes without `FAKE` suffix), and SSN-shaped strings outside the canonical `123-45-6789` placeholder.
