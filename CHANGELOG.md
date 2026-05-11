# Changelog

All notable changes to ScreenLeak.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

### Added
- `rfdetr` image adapter — wraps the local fine-tuned RF-DETR ONNX detector (`models/rfdetr_v8.onnx`, ~28M-param DINOv2-S + LWDETR head, 12-class, 320×320 input). Reads input size from the ONNX graph so we can swap in larger checkpoints (v2 at 384×384) without changing code. Uses CoreML EP on macOS where available, CPU otherwise.
- `vendor_image.sh` now copies `models/rfdetr_v8.onnx` (108 MB) into `image/models/` so the adapter runs end-to-end after a fresh vendor. `MODELS=skip` opts out.
- RF-DETR result on full 221-image val: **95.3% zero-leak**, 0.871 macro-F1, 0.970 micro-F1, p50 285ms — a 90-point gap over the best frontier vision model (Gemini 3.1 Pro at 4.2%).
- `gcp_dlp` adapter for **both** text and image benches — wraps Google Cloud DLP (Sensitive Data Protection) `inspect_content` with the same 40-infoType → 12-class label map shared across surfaces. Auth via Application Default Credentials; project from `GCP_DLP_PROJECT` or `gcloud config`. Image variant sends each PNG as `byte_item` (IMAGE_PNG) and harvests `image_location.bounding_boxes`.
- GCP DLP results: text **37.7% zero-leak** (95% CI 32.8–42.9%), image **2.6% zero-leak**. On text it sits between Presidio (35.4%) and base OPF (38.6%) — barely above regex (33.9%). On image it's statistically tied with `regex_ocr` (2.6%) and Claude Opus 4.7 (2.1%). The commercial cloud-DLP category is not competitive on screen-shaped data.

### Changed
- Headline section in `README` rewritten around the "frontier can name, in-distribution detector can box" finding. `LIMITATIONS.md` updated to flag that RF-DETR's val is distribution-matched (same generator), not out-of-distribution.
- README finding #1 now calls out commercial DLP (GCP DLP + Presidio) as a separate failure mode from frontier LLMs.
- `scripts/build_unified_leaderboard.py` knows about `rfdetr` and `gcp_dlp` (model-id mapping).

## [0.0.1] — 2026-05-10

Initial private staging release. Three sub-benches assembled, frontier-model adapters wired, first headline numbers landed.

### Added
- Repo skeleton + brand (ScreenLeak): `README`, `METHODOLOGY`, `THREAT_MODEL`, `CATEGORIES`, `LIMITATIONS`, `SOURCES`, `CITATION`, `ROADMAP`, `CONTRIBUTING`, `SECURITY`.
- `LICENSE` (Apache 2.0) for code and `LICENSE-DATA` (CC BY 4.0) for corpora.
- `text/` sub-bench: vendored from `screenpipe-pii-bench` (422 cases, 13 categories, 17 adapters including 3 new frontier API adapters: `claude`, `gpt5`, `gemini`).
- `image/` sub-bench: vendored from `screenpipe-pii-bench-image` (2,206 synthetic images across 9 templates, 4 adapter scaffolds, ~9MB subset).
- `trace/` sub-bench: built from scratch. `pii_pool.py` (97 synthetic items / 12 categories), `build_seeds.py`, `inject.py`, `replay.py`, `score.py`, adapters for Claude / GPT-5 / Gemini.
- Top-level `Makefile` with `vendor`, `bench`, `unify`, `smoke`, `test`, `lint`, `pre-oss`, `clean`.
- `scripts/vendor_text.sh`, `scripts/vendor_image.sh`, `scripts/build_unified_leaderboard.py`, `scripts/pre_oss_check.sh`.
- 31 unit tests covering pii pool, injection (gold-truthfulness, unicode handling, determinism), scorer (literal + fuzzy matching, bootstrap CIs), and unified-leaderboard parsing.
- GitHub CI workflow + issue / PR templates.
- `.synth-allowlist` for files deliberately containing synthetic-realistic strings.

### Frontier model defaults (current)

- `claude-opus-4-7`
- `gpt-5.5`
- `gemini-3.1-pro-preview`

### Trace replay protocol

After the last `tool` message, the replay appends a fixed user nudge:
> *"Based on what you found, give a brief summary or next step for the original request."*

Without the nudge, some models (notably Claude Opus 4.7) end the turn with zero content blocks because no explicit "now respond" cue was given. The nudge keeps the bench symmetric — every model produces something — without changing what counts as a leak (gold = PII embedded in the *tool result*, not the nudge).

### Adapter quirks worth remembering
- **Opus 4.7 deprecated `temperature`** — text and trace adapters omit it.
- **Gemini rejects `additionalProperties`** in `response_schema` — image/text Gemini adapters strip it.

### Image bench
- Existing baselines: `regex_ocr` 2.6% zero-leak, `presidio_image` 0.5%. Frontier models not yet scored (vision adapters slated for v0.1).

### Known limitations (carried into v0.1)
- Image bench category set is asymmetric vs text/trace (missing `private_handle`, `private_id`, `private_date`).
- Trace bench v0 covers unprompted leakage only; adversarial prompt-injection split slips to v0.1.
- Image bench shipped as 60-image subset (~9MB) rather than full 2,206 images. Full corpus uploads as HF dataset on public release.
- English-only on image and trace benches.
- No adapter for the screenpipe-pii-redactor model on image or trace benches (text bench only).
