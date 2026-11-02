#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""Run a text-to-text post-processing step (cleanup, reshape) through an external model
instead of the agent itself. The agent is the default executor; use this when the user
asks for a specific model, a cheaper one, or a local cleanup model.

  --endpoint openrouter  (default) OPENROUTER_API_KEY, any chat model
  --endpoint <base-url>  any OpenAI-compatible /v1/chat/completions server (e.g. a local
                         cleanup model such as S1-mini served by llama.cpp/vLLM/Ollama);
                         key from REWRITE_API_KEY if the server needs one

    uv run --script rewrite.py memo.raw.txt --prompt ../templates/prompts/cleanup-light.md -o memo.clean.md
    uv run --script rewrite.py memo.clean.md --prompt ../templates/reshape/dev-spec.md -o memo.spec.md \
        --model anthropic/claude-sonnet-5.5
    uv run --script rewrite.py memo.raw.txt --prompt cleanup-light.md --endpoint http://localhost:8080 --model s1-mini

Prints a JSON report (model, tokens, cost where reported, output path).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

DEFAULT_MODEL = "~google/gemini-flash-latest"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="text file to transform")
    ap.add_argument("--prompt", type=Path, required=True, help="system prompt file (a template)")
    ap.add_argument("--extra", default="", help="extra instructions appended to the system prompt")
    ap.add_argument("--endpoint", default="openrouter")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    if a.output.exists():
        print(json.dumps({"error": f"refusing to overwrite {a.output}"}))
        return 2
    system = a.prompt.read_text() + (f"\n\nAdditional instructions:\n{a.extra}" if a.extra else "")
    if a.endpoint == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            print(json.dumps({"error": "missing OPENROUTER_API_KEY"}))
            return 2
    else:
        url = a.endpoint.rstrip("/") + "/v1/chat/completions"
        key = os.environ.get("REWRITE_API_KEY")
    body = {"model": a.model, "temperature": 0.2,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": a.input.read_text()}]}
    if a.endpoint == "openrouter":
        body["usage"] = {"include": True}
    r = httpx.post(url, json=body, timeout=600, headers={"Authorization": f"Bearer {key}"} if key else {})
    if r.status_code != 200:
        print(json.dumps({"error": "request failed", "status": r.status_code, "body": r.text[:2000]}))
        return 1
    d = r.json()
    a.output.write_text(d["choices"][0]["message"]["content"].strip() + "\n")
    u = d.get("usage") or {}
    print(json.dumps({"output": str(a.output), "model": d.get("model", a.model), "prompt": str(a.prompt),
                      "tokens_in": u.get("prompt_tokens"), "tokens_out": u.get("completion_tokens"),
                      "cost_usd": u.get("cost")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
