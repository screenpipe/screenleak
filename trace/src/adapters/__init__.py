# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""Trace-bench adapters.

Each adapter exposes:

    complete(messages: list[dict], max_tokens: int = 2048) -> dict

The returned dict has keys:
    text:           the assistant message body
    tool_call_args: list of stringified tool-call argument blobs (may be empty)

Both are concatenated by replay.py into a single `agent_output` blob that
score.py scans for injected-PII leaks.
"""
