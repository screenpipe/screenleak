# ScreenLeak — https://github.com/screenpipe/screenleak
# SPDX-License-Identifier: Apache-2.0
"""Gemini 2.5 Pro adapter for trace-PII bench.

Translates OpenAI-style messages into google-genai's `Content` shape:
    user/assistant/tool messages -> contents[] with role + parts[]
    OpenAI tool_calls -> function_call parts
    OpenAI tool role  -> function_response parts

System messages are concatenated and sent as `system_instruction`.

Env:
    GOOGLE_API_KEY  required (or GEMINI_API_KEY)
    SCREENLEAK_GEMINI_MODEL  optional, default "gemini-3.1-pro-preview"
"""

from __future__ import annotations

import json
import os
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise ImportError(
        "google-genai SDK not installed. Run: pip install google-genai"
    ) from e


_CLIENT: Any = None


def _client() -> Any:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get(
            "GEMINI_API_KEY"
        )
        _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _to_gemini(messages: list[dict]) -> tuple[str, list[Any]]:
    system_parts: list[str] = []
    contents: list[Any] = []

    for m in messages:
        role = m.get("role")
        if role == "system":
            if m.get("content"):
                system_parts.append(m["content"])
            continue
        if role == "user":
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=m.get("content") or "")],
            ))
            continue
        if role == "assistant":
            parts: list[Any] = []
            if m.get("content"):
                parts.append(types.Part(text=m["content"]))
            for tc in m.get("tool_calls") or []:
                fn = tc.get("function") or {}
                args = fn.get("arguments")
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {"_raw": args}
                parts.append(types.Part(
                    function_call=types.FunctionCall(
                        name=fn.get("name") or "tool",
                        args=args or {},
                    )
                ))
            if parts:
                contents.append(types.Content(role="model", parts=parts))
            continue
        if role == "tool":
            content_str = m.get("content") or ""
            try:
                resp_obj = json.loads(content_str)
                if not isinstance(resp_obj, dict):
                    resp_obj = {"result": resp_obj}
            except Exception:
                resp_obj = {"result": content_str}
            contents.append(types.Content(
                role="user",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name="tool",
                        response=resp_obj,
                    )
                )],
            ))
            continue

    return "\n\n".join(system_parts), contents


def complete(messages: list[dict], max_tokens: int = 2048) -> dict:
    """Replay the trace and return the model's continuation."""
    model = os.environ.get("SCREENLEAK_GEMINI_MODEL", "gemini-3.1-pro-preview")
    system, contents = _to_gemini(messages)

    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        system_instruction=system or None,
    )

    resp = _client().models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    text_parts: list[str] = []
    tool_call_args: list[str] = []
    for cand in resp.candidates or []:
        for part in (cand.content.parts if cand.content else []):
            if getattr(part, "text", None):
                text_parts.append(part.text)
            if getattr(part, "function_call", None):
                tool_call_args.append(
                    json.dumps(dict(part.function_call.args or {}))
                )

    return {"text": "\n".join(text_parts), "tool_call_args": tool_call_args}
