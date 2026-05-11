# Contributing to ScreenLeak

ScreenLeak is research infrastructure. We welcome contributions that:

- **Add a new adapter** so a new model (or a new revision of an existing model) appears on the leaderboard.
- **Extend the corpus** with new categories, new templates, new languages, or adversarial splits.
- **Improve scoring** by tightening or correcting the methodology.
- **Find bugs** in injection, scoring, or vendor scripts.

We do **not** accept:

- Vendor-marketing PRs framing ScreenLeak as a sales tool for any product.
- Adapters that wrap closed-source services without published model identifiers (we require named, citable model IDs).
- Real-PII corpus contributions. All bench data is synthetic.

## Quick start

```bash
git clone https://github.com/screenpipe/screenleak
cd screenleak
make install
make test       # 31 unit tests should pass
make smoke      # end-to-end pipeline smoke test (no API calls)
```

## Adding an adapter

Each sub-bench (text, image, trace) has its own adapter shape:

### Text adapter

```python
# text/src/adapters/your_model.py
LABEL_MAP = {}  # adapter is told to use bench labels directly

def redact(text: str) -> list[dict]:
    """Return [{start, end, label, text}, ...] spans found in the input."""
    ...
```

Drop into `text/src/adapters/`, then run:

```bash
make bench-text TEXT_ARGS="--adapter your_model"
```

### Image adapter

```python
# image/src/adapters/your_model.py
def setup() -> None: ...   # raise if deps/keys missing — score harness will skip
def predict(image_path: str) -> list[dict]:
    """Return [{bbox: [x,y,w,h], label, confidence?}, ...] for one image."""
    ...
```

### Trace adapter

```python
# trace/src/adapters/your_model.py
def complete(messages: list[dict], max_tokens: int = 2048) -> dict:
    """Return {'text': '...', 'tool_call_args': ['...']}."""
    ...
```

## Submitting a leaderboard entry

When you add an adapter and run the bench:

1. Run the full bench: `make bench-text` / `bench-image` / `bench-trace`
2. Commit `<sub-bench>/results/leaderboard.md` (regenerated automatically)
3. Run `make unify` to refresh `results/unified_leaderboard.md`
4. Open a PR with a short note on:
   - What the model is (provider, version, parameter count if open)
   - Compute used (API region, hardware for local)
   - Any prompt or post-processing tweaks

We expect adapter PRs to include the leaderboard refresh — submitters demonstrate they ran the bench rather than asking maintainers to.

## Filing an issue

Use one of the templates under `.github/ISSUE_TEMPLATE/`. Include:

- The exact `make` command that reproduced the issue
- Adapter name, model id, env vars set
- Output of `python -m trace.src.pii_pool` (if PII-pool relevant)

## Provenance discipline

Two repos contribute data: `screenpipe-pii-bench` (text) and `screenpipe-pii-bench-image` (image). The `text/` and `image/` directories here are **vendored snapshots** — running `make vendor` copies fresh from the source repos.

When you change something in `text/src/` or `image/src/`, **make the change in the source repo first**, then re-vendor. Otherwise the next vendor run silently overwrites your edit. The vendor scripts emit the source commit into `<bench>/PROVENANCE.md` — use that to know what you're working from.

The `trace/` directory is built fresh in this repo. Edit there directly.

## Code style

- Python ≥ 3.10
- Ruff: `make lint`
- Type hints on public APIs
- No multi-paragraph docstrings; one short line for `WHY`, not `WHAT`

## Code of conduct

Be useful, be precise, don't waste people's time. If you're unsure whether a contribution is in scope, open an issue first to discuss.
