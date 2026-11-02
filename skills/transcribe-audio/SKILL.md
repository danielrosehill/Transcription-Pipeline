---
name: transcribe-audio
description: Turn audio into a raw transcript with one ASR backend - OpenRouter audio models (default, latest Gemini Flash, or a model slot from preferences), AssemblyAI (long-form, timestamps, speaker labels), Gemini direct (long files via Files API), or a local/self-hosted OpenAI-compatible server (Whisper, Parakeet). Saves the provider's output untouched. Use on "transcribe", "use AssemblyAI", "use or2", "run it on my server", "with timestamps".
---

# Transcribe audio

```bash
uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/transcribe.py <file-or-url> \
  [--backend openrouter|assemblyai|gemini|local] [--model <id>] [--mode raw|light | --prompt-file <f>] \
  [--speakers N | --diarize] [--timestamps] [--language en] [--local-url <url>] [--out-dir <dir>] [--stem <name>]
```

Writes `<stem>.raw.txt` (always), `<stem>.raw.srt` (timestamps), `<stem>.raw.json` (full provider response),
`<stem>.meta.json` (backend, model asked for and actually used, elapsed, cost, words), and prints the meta.
Keys come from the environment; if the user's preferences say keys live behind a runner or under other names,
wrap the command accordingly (e.g. `OPENROUTER_API_KEY=$OTHER_NAME uv run ...`).

## Pick the backend

| Situation | Backend | Details |
|---|---|---|
| Everyday voice notes | `openrouter` (default) | `references/openrouter.md` |
| Long recordings (20 min+), timestamps/subtitles, several speakers | `assemblyai` | `references/assemblyai.md` |
| Long file, Gemini wanted, no OpenRouter key | `gemini` | `references/gemini.md` |
| User asks for local, private or their own server | `local` | `references/local.md` |
| User names a slot (`or2`), a model or a server | per the preferences tables | |

`--mode raw` (default) asks LLM backends for a verbatim transcript; `--mode light` removes disfluencies at
transcription time (one pass, cheaper, but there is then no true raw). Prefer raw + `clean-transcript` when the
user wants both versions, which is the default. Prompts are in `templates/prompts/`; a user can point
`--prompt-file` at their own. Add vocabulary hints from the preferences to a custom prompt when the
recording is full of names or jargon.

If a backend fails twice, say how, and offer the next one in the table rather than retrying the same call.
