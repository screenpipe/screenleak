# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""GPT-5 adapter for trace-PII bench.

The trace bench traces are already in OpenAI tool-call format, so this
adapter passes them through to the chat.completions endpoint with minimal
translation. We DO NOT pass a `tools=[...]` schema because the seed
traces' tool calls are reads-only retrieval calls; the agent's "next move"
is allowed to be either text or another tool call.

Env:
    OPENAI_API_KEY  required
    SCREENLEAK_GPT5_MODEL  optional, default "gpt-5.5"
"""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from openai import OpenAI
except ImportError as e:
    raise ImportError(
        "openai SDK not installed. Run: pip install openai"
    ) from e


_CLIENT: Any = None


def _client() -> Any:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI()
    return _CLIENT


def complete(messages: list[dict], max_tokens: int = 2048) -> dict:
    """Replay the trace and return the model's continuation."""
    model = os.environ.get("SCREENLEAK_GPT5_MODEL", "gpt-5.5")

    # Sanitize: ensure tool_calls have stringified arguments (OpenAI strict)
    cleaned: list[dict] = []
    for m in messages:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            tcs = []
            for tc in m["tool_calls"]:
                fn = tc.get("function") or {}
                args = fn.get("arguments")
                if not isinstance(args, str):
                    args = json.dumps(args or {})
                tcs.append({
                    "id": tc.get("id") or "tc1",
                    "type": "function",
                    "function": {
                        "name": fn.get("name") or "tool",
                        "arguments": args,
                    },
                })
            cleaned.append({
                "role": "assistant",
                "content": m.get("content") or "",
                "tool_calls": tcs,
            })
        else:
            cleaned.append(m)

    resp = _client().chat.completions.create(
        model=model,
        messages=cleaned,
        max_completion_tokens=max_tokens,
    )

    msg = resp.choices[0].message
    text = msg.content or ""
    tool_call_args: list[str] = []
    for tc in (msg.tool_calls or []):
        args = (tc.function.arguments or "") if tc.function else ""
        tool_call_args.append(args)

    return {"text": text, "tool_call_args": tool_call_args}
