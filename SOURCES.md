# Sources

Provenance for every vendored asset in this repo. Updated whenever vendor scripts run.

## What "vendored" means here

`text/` and `image/` are **copies** of in-house repos that already exist. We copy (not symlink, not submodule) so this repo is a single shippable artifact when it goes public.

`trace/` is **built fresh** in this repo. It pulls seed traces from `screenpipe-finetune` but re-shapes them; the source data is referenced, not vendored.

The vendor scripts (`scripts/vendor_text.sh`, `scripts/vendor_image.sh`) record the source commit hash + timestamp into `<sub-bench>/PROVENANCE.md` so we never lose the lineage.

## text/

| Field | Value |
|---|---|
| Source repo | `~/Documents/screenpipe-pii-bench` (private, in-house) |
| Vendor script | `scripts/vendor_text.sh` |
| Last vendor | (see `text/PROVENANCE.md` after first run) |
| Original license | Apache 2.0 |

What gets copied:
- `data/*.jsonl` — 19 hand-crafted JSONL files, 422 cases
- `src/` — adapters + scoring code
- `CATEGORIES.md`, `METHODOLOGY.md`, `LIMITATIONS.md`, `THREAT_MODEL.md`, `MODEL_CARD.md` — vendored under `text/docs/` to avoid clobbering the unified versions in repo root
- `results/leaderboard.md` — copied to `text/results/`

What does NOT get copied:
- `training/` — the data-generation Ralph loop. This is operational tooling, not part of the bench. Stays in the source repo.
- `triage/` — debugging scratch space. Same.

## image/

| Field | Value |
|---|---|
| Source repo | `~/Documents/screenpipe-pii-bench-image` (private, in-house) |
| Vendor script | `scripts/vendor_image.sh` |
| Last vendor | (see `image/PROVENANCE.md` after first run) |
| Original license | TBD upstream — defaults to Apache 2.0 in this repo |

What gets copied:
- `corpus/annotations*.jsonl` — annotation files (small, ~few MB)
- `corpus/images_002/` — 2000 PNG screenshots (~180 MB) — see "Image data weight" below
- `templates/` — HTML/CSS templates per app
- `src/` — adapters + scoring code
- `STATUS.md` — copied to `image/docs/` for context

What does NOT get copied:
- `training/` — spec-batch generators. Stays in source.
- `_smoke_out/` — debug artifacts.
- `node_modules/` — never vendor these.
- `rust_smoke/` — sandbox.

### Image data weight

180 MB of PNGs is OK for a private repo but is on the borderline for OSS. Two strategies:

1. **Keep the PNGs in the repo** (with Git LFS). Most reproducible. Tradeoff: heavier clone.
2. **Ship annotations + regen script**, omit PNGs. Smallest repo. Tradeoff: requires Playwright + Chromium to reproduce.

**v0 plan:** ship annotations + a small representative subset (~50 images) + the regen script. The full 2000-image corpus uploads as an HF dataset (`screenpipe/screenleak-image`). Cleanest split for OSS audiences.

## trace/

| Field | Value |
|---|---|
| Source data | `~/Documents/screenpipe-finetune/data/screenpipe_raw.jsonl` (18,387 rows) |
| Source repo (training pipeline) | `~/Documents/screenpipe-finetune` (private, in-house) |
| Vendor script | (built in-tree by `trace/src/build_seeds.py` once written) |
| License | Same as the rest of this repo |

We pull 50–100 seed traces from `screenpipe_raw.jsonl`, inject labeled PII into the simulated tool-result content, and store as `trace/data/seeds.jsonl`. The source 18K-row dataset itself is **not** vendored — too large, mostly irrelevant, contains scrub-resistant code-style content.

The injected traces in `trace/data/` are the asset. Source data is just the seed pool.

## What's intentionally NOT here

- The `~/Documents/screenshots/` corpus (13 GB of real Louis-machine recordings). Stays private forever. ScreenLeak is synthetic-only.
- The `screenpipe-pii-redactor` model itself. Lives on HF as `screenpipe/pii-redactor` (CC BY-NC 4.0). The text bench has an adapter that runs it; the model is not in this repo.
- The `opf-rs` Rust runtime. Separate engineering artifact, separate launch. The text bench's `opf_rs` adapter reads precomputed predictions from a path the user controls.
- Any real PII. All names, emails, phone numbers, addresses, etc. in the bench are synthetic / fictional.
