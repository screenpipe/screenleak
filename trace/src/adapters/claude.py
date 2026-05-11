# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""Claude adapter for trace-PII bench.

Replays an OpenAI-style trace against the Anthropic Messages API. Translates:
    OpenAI tool_calls -> Anthropic tool_use content blocks
    OpenAI tool role  -> Anthropic tool_result content blocks

Returns the model's continuation as {"text", "tool_call_args"}.

Env:
    ANTHROPIC_API_KEY  required
    SCREENLEAK_CLAUDE_MODEL  optional, default "claude-opus-4-7"
"""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from anthropic import Anthropic
except ImportError as e:
    raise ImportError(
        "anthropic SDK not installed. Run: pip install anthropic"
    ) from e


_CLIENT: Any = None


def _client() -> Any:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = Anthropic()
    return _CLIENT


def _to_anthropic(messages: list[dict]) -> tuple[str, list[dict]]:
    """Convert OpenAI-style messages to (system, messages) for Anthropic.

    The trace bench traces use OpenAI tool-call format (assistant.tool_calls,
    role=tool, tool_call_id). We translate to Anthropic's content-block shape.
    """
    system_parts: list[str] = []
    out: list[dict] = []
    pending_tool_results: list[dict] = []

    def flush_tool_results():
        nonlocal pending_tool_results
        if pending_tool_results:
            out.append({"role": "user", "content": pending_tool_results})
            pending_tool_results = []

    for m in messages:
        role = m.get("role")
        if role == "system":
            content = m.get("content") or ""
            if content:
                system_parts.append(content)
            continue
        if role == "user":
            flush_tool_results()
            out.append({"role": "user", "content": m.get("content") or ""})
            continue
        if role == "assistant":
            flush_tool_results()
            blocks: list[dict] = []
            text = m.get("content") or ""
            if text:
                blocks.append({"type": "text", "text": text})
            for tc in m.get("tool_calls") or []:
                fn = tc.get("function") or {}
                args = fn.get("arguments")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {"_raw": args}
                blocks.append({
                    "type": "tool_use",
                    "id": tc.get("id") or "tool_use",
                    "name": fn.get("name") or "tool",
                    "input": args or {},
                })
            if blocks:
                out.append({"role": "assistant", "content": blocks})
            continue
        if role == "tool":
            pending_tool_results.append({
                "type": "tool_result",
                "tool_use_id": m.get("tool_call_id") or "tool_use",
                "content": m.get("content") or "",
            })
            continue

    flush_tool_results()
    return "\n\n".join(system_parts), out


def complete(messages: list[dict], max_tokens: int = 2048) -> dict:
    """Replay the trace and return the model's continuation."""
    model = os.environ.get("SCREENLEAK_CLAUDE_MODEL", "claude-opus-4-7")
    system, msgs = _to_anthropic(messages)
    resp = _client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system or None,
        messages=msgs,
    )

    text_parts: list[str] = []
    tool_call_args: list[str] = []
    for block in resp.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_call_args.append(json.dumps(block.input or {}))

    return {
        "text": "\n".join(text_parts),
        "tool_call_args": tool_call_args,
    }
