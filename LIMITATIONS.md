# Limitations

What ScreenLeak doesn't measure, doesn't cover, or measures imperfectly. Updated honestly per release.

## v0 (current)

### Synthetic data only

- All three sub-benches are synthetic. No real user data was used in any corpus.

**Synthetic-domain caveat.** The bench uses plausibly-realistic email domains rather than reserved ones — otherwise a redactor that learned to skip placeholder-style domains would game the bench trivially. As a side effect, some synthetic domains coincidentally collide with real-but-unrelated organizations. The local-parts are synthetic and we make no claim that any email in the corpus belongs to a real person. If a collateral collision matters to your organization, email `louis@screenpi.pe` for a swap.

**Why this matters:** frontier models may overfit to in-distribution UI shapes. A model that scores 90 % zero-leak on `image/` may still leak on a real Slack screenshot with anti-aliasing artifacts, third-party browser extensions, or unusual font rendering. Real-screen validation is on the v1.0 roadmap; until then, treat the absolute image-bench numbers as best-case (in-distribution) figures, and the *relative* ordering of adapters as the load-bearing signal.

### Category asymmetry

The image bench corpus does not contain spans for these canonical categories:

- `private_handle`
- `private_id`
- `private_date`

Interpret the image bench numbers as "9-of-13 categories" rather than fully comparable to text bench. Backport is on the v0.1 roadmap.

### English-heavy

- Text bench has multilingual splits (Japanese, Korean, French, Spanish, Italian, German, Dutch).
- Image bench is **English-only** in v0. No CJK / Cyrillic / Arabic / RTL coverage.
- Trace bench is **English-only**.

Multi-script image bench is slated for post-v0.1.

### Adversarial coverage

- Text bench has dedicated adversarial splits covering control characters, unicode tricks, and format-mimicry attacks.
- Image bench has hard negatives but no dedicated adversarial split.
- Trace bench v0 covers **unprompted leakage only**. Adversarial prompt-injection via on-screen text is slated for v0.1.

### Trace bench is small

50 traces total in v0 (25 train + 25 val); the leaderboard scores against the val split. With n=25 the 95 % bootstrap CIs are ~ ±20 percentage points wide — the ranking is suggestive, not decisive between adjacent rows. v0.1 scales the corpus to 200 (val 100).

### Image bench: GPT-5.5 is slow

GPT-5.5's vision API was slow enough (per-image latency dominated by reasoning) that the original run took ~80 minutes for 221 images. All three frontier models are scored on the full 221-image val split, but reproducing the GPT-5.5 row may require similar patience or rate-limit handling depending on your account tier.

### Image bench: rfdetr is in-distribution

The local `rfdetr_v8` checkpoint was trained on the same source distribution the image bench evaluates against. The val split is image-disjoint (no leaked PNGs) but distribution-matched. Its 95.3 % zero-leak therefore measures **in-distribution recall**, not out-of-distribution generalization. Read it as: "what's achievable on this exact surface when you can train on the source." It does *not* claim anything about arbitrary real Slack / Outlook / Cursor screenshots. We expect the gap to narrow materially on real-screen evaluation — that's a v1.0 deliverable.

### Frozen leaderboard

v0 ships with a single-snapshot leaderboard. No automated CI / live refresh. Models change weekly (especially frontier APIs) — re-run is manual until v0.2.

### No capability measurement

ScreenLeak measures disclosure, not capability. A model that refuses to do anything will score 100 % zero-leak on trace bench and is also useless. Capability is measured elsewhere (WebArena, OSWorld, GAIA).

## Per-sub-bench limitations

See:
- `text/LIMITATIONS.md` — span-matching edge cases, label-space disagreements with upstream OPF
- `image/STATUS.md` — template diversity, adapter coverage gaps
- `trace/README.md` — injection-pipeline caveats (once built)

## What we'll fix in v0.1

- Image bench category coverage (add `private_handle`, `private_id`, `private_date`)
- Trace bench adversarial-injection split
- Trace bench size: 50 → 200
- One more frontier-model refresh

## What we won't fix in v1.x

- Real-user-data corpus. Privacy + legal + provenance complexity. Synthetic is the long-term plan.
- OS-level keystroke / sudo-prompt leak measurement. Out of scope.
- Internal-reasoning / CoT leakage measurement. APIs don't expose this consistently.
