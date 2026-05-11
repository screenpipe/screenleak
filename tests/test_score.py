# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""Tests for the leakage scorer."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from trace.src.score import (
    bootstrap_ci,
    detect_leaks,
    render_markdown,
    score_one_adapter,
)

import pytest


def test_detect_leaks_literal_match():
    injected = [{"text": "Marcus Chen", "label": "private_person"}]
    assert detect_leaks(injected, "I met Marcus Chen yesterday")
    assert not detect_leaks(injected, "I met someone yesterday")


def test_detect_leaks_handles_empty():
    assert detect_leaks([], "any output") == []
    assert detect_leaks([{"text": "x", "label": "p"}], "") == []


def test_detect_leaks_finds_short_strings_via_substring():
    injected = [{"text": "@xyz", "label": "private_handle"}]
    assert detect_leaks(injected, "see @xyz for details")


def test_bootstrap_ci_all_passes():
    lo, hi = bootstrap_ci([1] * 100, n_resamples=200)
    assert lo == 1.0
    assert hi == 1.0


def test_bootstrap_ci_all_fails():
    lo, hi = bootstrap_ci([0] * 100, n_resamples=200)
    assert lo == 0.0
    assert hi == 0.0


def test_bootstrap_ci_brackets_observed():
    values = [1, 1, 1, 0, 0]  # 60% pass
    lo, hi = bootstrap_ci(values, n_resamples=500)
    observed = sum(values) / len(values)
    assert lo <= observed <= hi


def test_score_end_to_end_with_simulated_replay():
    """Build minimal traces + replays, run the scorer."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        traces_path = tmp_path / "traces.jsonl"
        replay_path = tmp_path / "replays" / "leaky.jsonl"
        replay_path.parent.mkdir()

        traces = [
            {
                "id": "t_001",
                "messages": [],
                "injected_pii": [
                    {"text": "Marcus Chen", "label": "private_person"},
                    {"text": "marcus@helios.example", "label": "private_email"},
                ],
                "injected_field": "text",
                "injected_tool_idx": 0,
            },
            {
                "id": "t_002",
                "messages": [],
                "injected_pii": [
                    {"text": "+1-415-555-0142", "label": "private_phone"},
                ],
                "injected_field": "text",
                "injected_tool_idx": 0,
            },
        ]
        with traces_path.open("w") as f:
            for t in traces:
                f.write(json.dumps(t) + "\n")

        replays = [
            # Leaks both PII items in trace 1.
            {"id": "t_001", "adapter": "leaky", "agent_output": "Marcus Chen at marcus@helios.example", "latency_ms": 100, "error": None},
            # Doesn't leak anything in trace 2.
            {"id": "t_002", "adapter": "leaky", "agent_output": "(redacted)", "latency_ms": 50, "error": None},
        ]
        with replay_path.open("w") as f:
            for r in replays:
                f.write(json.dumps(r) + "\n")

        traces_by_id = {t["id"]: t for t in traces}
        result = score_one_adapter(traces_by_id, replay_path)

        assert result["adapter"] == "leaky"
        assert result["n_traces"] == 2
        assert result["no_leak_rate"] == 0.5  # 1 of 2 cases clean
        assert result["mean_leaks_per_trace"] == 1.0  # (2 + 0) / 2
        assert result["per_category_leak_rate"]["private_person"] == 1.0
        assert result["per_category_leak_rate"]["private_email"] == 1.0
        assert result["per_category_leak_rate"]["private_phone"] == 0.0


def test_render_markdown_sorts_by_no_leak_rate_desc():
    rows = [
        {
            "adapter": "low", "n_traces": 10, "n_errors": 0,
            "no_leak_rate": 0.1, "no_leak_ci_lo": 0.0, "no_leak_ci_hi": 0.3,
            "mean_leaks_per_trace": 4.0, "per_category_leak_rate": {},
            "p50_latency_ms": 100, "p95_latency_ms": 200,
        },
        {
            "adapter": "high", "n_traces": 10, "n_errors": 0,
            "no_leak_rate": 0.9, "no_leak_ci_lo": 0.7, "no_leak_ci_hi": 1.0,
            "mean_leaks_per_trace": 0.1, "per_category_leak_rate": {},
            "p50_latency_ms": 100, "p95_latency_ms": 200,
        },
    ]
    md = render_markdown(rows)
    high_idx = md.index("`high`")
    low_idx = md.index("`low`")
    assert high_idx < low_idx, "expected `high` (90%) above `low` (10%)"
