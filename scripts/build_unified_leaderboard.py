# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""
build_unified_leaderboard.py — combine per-sub-bench leaderboards into one.

Reads:
    text/results/leaderboard.md   (existing format, parsed for adapter zero-leak)
    image/results/leaderboard.md  (existing format)
    trace/results/leaderboard.md  (built by trace/src/score.py)

Writes:
    results/unified_leaderboard.md

Output shape:
    | Model | Text zero-leak | Image zero-leak | Trace no-leak | Local? |

If a model is missing from a sub-bench, the cell is "—". This is expected
in v0 because the three sub-benches don't share an adapter taxonomy yet.

This script is intentionally simple: regex-parses markdown tables, no
brittle leaderboard schema. Easy to evolve later.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HEADER_RE = re.compile(r"^\|\s*Adapter\s*\|", re.IGNORECASE)
ROW_RE = re.compile(r"^\|\s*`?(?P<adapter>[^`|]+?)`?\s*\|\s*(?P<score>[\d.]+)%")


def parse_leaderboard(path: Path) -> dict[str, float]:
    """Return {adapter -> zero-leak %} from a sub-bench leaderboard markdown.

    Reads ONLY the first markdown table (the headline leaderboard). Per-category
    tables further down would otherwise overwrite the headline scores with their
    first-column percentage, which is wrong (e.g. trace's `claude` shows 96% in
    the headline but 0% in the first per-category cell).
    """
    if not path.exists():
        return {}
    rows: dict[str, float] = {}
    for line in path.read_text().splitlines():
        # New section header — stop parsing the headline table.
        if line.startswith("## "):
            break
        m = ROW_RE.match(line)
        if not m:
            continue
        adapter = m.group("adapter").strip()
        # Don't overwrite — first occurrence wins (same defensive guarantee).
        if adapter not in rows:
            rows[adapter] = float(m.group("score"))
    return rows


# Hint: which adapters are "local" vs API. Adjust as adapters are added.
LOCAL = {
    "regex", "regex_ocr", "presidio", "presidio_image",
    "opf_rs", "privacy_filter", "privacy_filter_ft",
    "privacy_filter_ft_v2", "privacy_filter_ft_v3",
    "privacy_filter_ft_v4", "privacy_filter_ft_v5",
    "gliner_pii", "moondream", "gemma4", "pixtral", "llama4",
    "rfdetr",
}

# Adapter name -> default model id. Reflects what runs when the adapter is
# invoked with no env override. Update when the adapter defaults change.
ADAPTER_MODELS = {
    "claude": "claude-opus-4-7",
    "gpt5": "gpt-5.5",
    "gemini": "gemini-3.1-pro-preview",
    "opf_rs": "screenpipe/pii-redactor (1.4B MoE NER, fine-tune)",
    "privacy_filter": "openai/privacy-filter (1.5B / 50M-active, base)",
    "privacy_filter_ft_v2": "screenpipe/pii-redactor v2 (fine-tune)",
    "privacy_filter_ft_v3": "screenpipe/pii-redactor v3 (fine-tune)",
    "gliner_pii": "urchade/gliner_multi_pii-v1",
    "moondream": "vikhyatk/moondream2 (rev 2025-06-21)",
    "gemma4": "google/gemma-4-E2B-it",
    "regex": "(deterministic baseline, no model)",
    "regex_ocr": "Tesseract OCR + 16 regex (deterministic baseline)",
    "presidio": "microsoft/presidio-analyzer",
    "presidio_image": "microsoft/presidio-image-redactor",
    "rfdetr": "screenpipe/rfdetr_v8 (DINOv2-S + LWDETR, 12-class, local fine-tune)",
    "gcp_dlp": "Google Cloud DLP / Sensitive Data Protection (cloud API)",
    "layered": "(stacked baseline)",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    out_path = args.out or (args.root / "results" / "unified_leaderboard.md")

    text_scores = parse_leaderboard(args.root / "text" / "results" / "leaderboard.md")
    image_scores = parse_leaderboard(args.root / "image" / "results" / "leaderboard.md")
    trace_scores = parse_leaderboard(args.root / "trace" / "results" / "leaderboard.md")

    all_adapters = sorted(
        set(text_scores) | set(image_scores) | set(trace_scores),
        key=lambda a: (
            -(trace_scores.get(a, -1)),  # rank trace winners first
            -(image_scores.get(a, -1)),
            -(text_scores.get(a, -1)),
        ),
    )

    lines = [
        "# ScreenLeak — Unified Leaderboard",
        "",
        "Higher is better across all three columns. \"—\" = adapter not run on that sub-bench. See per-sub-bench tables for CIs and per-category breakdowns.",
        "",
        "| Model | Text zero-leak | Image zero-leak | Trace no-leak | Local? |",
        "|---|---:|---:|---:|:---:|",
    ]
    for a in all_adapters:
        local = "✅" if a in LOCAL else "❌"
        t = f"{text_scores[a]:.1f}%" if a in text_scores else "—"
        i = f"{image_scores[a]:.1f}%" if a in image_scores else "—"
        tr = f"{trace_scores[a]:.1f}%" if a in trace_scores else "—"
        lines.append(f"| `{a}` | {t} | {i} | {tr} | {local} |")
    lines.append("")
    lines.append("## Adapter → model")
    lines.append("")
    lines.append("| Adapter | Model id |")
    lines.append("|---|---|")
    for a in all_adapters:
        model_id = ADAPTER_MODELS.get(a, "_unmapped — see adapter source_")
        lines.append(f"| `{a}` | `{model_id}` |")
    lines.append("")
    lines.append("_Per-sub-bench leaderboards: [text](../text/results/leaderboard.md), [image](../image/results/leaderboard.md), [trace](../trace/results/leaderboard.md)._")
    lines.append("")
    lines.append("_See [METHODOLOGY.md](../METHODOLOGY.md) for scoring rules and [LIMITATIONS.md](../LIMITATIONS.md) for caveats._")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    print(f"unified leaderboard -> {out_path}")
    print(f"  text adapters:  {len(text_scores)}")
    print(f"  image adapters: {len(image_scores)}")
    print(f"  trace adapters: {len(trace_scores)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
