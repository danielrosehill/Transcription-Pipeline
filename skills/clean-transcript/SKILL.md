---
name: clean-transcript
description: Clean a raw ASR transcript into a readable one without losing anything - light (remove disfluencies, resolve self-corrections, punctuation, paragraphs) or heavy (also headings, de-duplication, reordering of passages the speaker flagged as out of order, and marked fixes of likely mistranscriptions). Done by the agent by default or sent to a chosen model. Always keeps the raw. Use on "clean this up", "remove the ums", "tidy the transcript", "fix what it misheard".
---

# Clean a transcript

Input: `<stem>.raw.txt` (or any transcript). Output: `<stem>.clean.md` next to it. The raw file is never edited.

| Level | Prompt | What it does |
|---|---|---|
| `light` (default) | `templates/prompts/cleanup-light.md` | fillers, repetitions, false starts and self-corrections, punctuation, paragraphs. Nothing else. |
| `heavy` | `templates/prompts/cleanup-heavy.md` | light, plus `##` headings, removes repeated points, moves passages the speaker said were out of order, replaces probable ASR mistranscriptions, each marked `[corrected: x -> y]` |

Heavy is the riskiest step in the plugin because it changes words. Use it when asked, and keep its markers so
the user can audit; strip them only on request. Add the **Vocabulary** list from the user's preferences to the
heavy prompt: it is the best evidence of what a misheard word should have been.

## Executor

- **Agent (default):** read the prompt file, apply it to the transcript yourself, write `<stem>.clean.md`.
  Long transcripts: work section by section and do not drop or summarise any part; compare word counts at the end
  (light should keep roughly 85-100% of the raw words).
- **External model** when the user or preferences name one (`openrouter:<model>`, or a local OpenAI-compatible
  server running a cleanup model):
  ```bash
  uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/rewrite.py <stem>.raw.txt \
    --prompt ${CLAUDE_PLUGIN_ROOT}/templates/prompts/cleanup-light.md -o <stem>.clean.md \
    [--model <openrouter-model>] [--endpoint <base-url> --model <id>] [--extra "<vocabulary or instructions>"]
  ```
  Small dedicated cleanup models can need their own exact system prompt; if the preferences give one, use it with
  `--prompt` instead of the shipped file.

For diarized transcripts, keep the speaker labels exactly; run `label-speakers` before or after, not instead.
