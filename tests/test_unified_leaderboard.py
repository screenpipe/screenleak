# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""Tests for unified leaderboard parser."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# `scripts/` isn't a package; load build_unified_leaderboard.py directly.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_unified_leaderboard as bul  # noqa: E402  (sys.path setup above)

SAMPLE_LEADERBOARD = """# Leaderboard

| Adapter | Zero-leak (95% CI) | Oversmash | Easy | Medium | Hard |
|---|---:|---:|---:|---:|---:|
| `privacy_filter_ft_v3` | 79.4% (75.1%-83.8%) | 7.8% | 91% | 79% | 70% |
| `opf_rs` | 75.9% (71.6%-80.6%) | 7.8% | 86% | 77% | 61% |
| `regex` | 33.9% (28.7%-38.8%) | 1.3% | 31% | 37% | 18% |
"""


def test_parse_leaderboard_extracts_adapter_and_zero_leak():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "lb.md"
        path.write_text(SAMPLE_LEADERBOARD)
        scores = bul.parse_leaderboard(path)
    assert scores == {
        "privacy_filter_ft_v3": 79.4,
        "opf_rs": 75.9,
        "regex": 33.9,
    }


def test_parse_missing_file_returns_empty():
    scores = bul.parse_leaderboard(Path("/nonexistent/leaderboard.md"))
    assert scores == {}


def test_parse_skips_separator_and_header_rows():
    """The `|---|---:|` separator and header row must not parse as adapter rows."""
    md = """| Adapter | Zero-leak |
|---|---:|
| `foo` | 50.0% |
"""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "lb.md"
        path.write_text(md)
        scores = bul.parse_leaderboard(path)
    assert scores == {"foo": 50.0}


def test_local_set_includes_known_local_adapters():
    """Sanity: anything currently scored locally is in LOCAL."""
    must_be_local = {"regex", "regex_ocr", "presidio", "opf_rs"}
    assert must_be_local <= bul.LOCAL
