---
name: reshape-transcript
description: Rewrite a cleaned transcript into another document type - development spec or brief, notes, summary, meeting minutes, to-do list, email, blog outline, blog post, or any format the user describes or has saved as a template. Keeps the transcript files and adds the new one. Use on "turn this into a spec", "make minutes", "pull out the to-dos", "write it up as a blog post", or any "turn this into X".
---

# Reshape a transcript

Input: normally `<stem>.clean.md` (fall back to the raw one). Output: `<stem>.<suffix>.md`, alongside the others.

## Templates

Look in this order, first match wins:
1. `<prefs>/templates/<name>.md` (the user's own; path in the `setup` skill)
2. `${CLAUDE_PLUGIN_ROOT}/templates/reshape/<name>.md`

Shipped: `dev-spec` (suffix `spec`), `notes`, `summary`, `minutes`, `todo`, `email`, `blog-outline`, `blog-post`.

No template fits? Write the instruction from the request ("one-page brief for my accountant, formal") and use it
as the prompt. If the user is likely to ask for it again, offer to save it to `<prefs>/templates/`.

## Executor

- **Agent (default):** apply the template to the transcript yourself.
- **External model** if named: `scripts/rewrite.py <input> --prompt <template> -o <output> [--model ...] [--extra "..."]`.

## Rules

- Never invent content; everything in the output must trace back to the transcript. Gaps go in an "Open questions"
  or "To research" section, not into the text.
- Spoken order is not document order: put things where they belong (a dev spec follows build order).
- When the speaker contradicted themselves, keep the later statement and flag the contradiction.
- Several reshapes from one transcript are fine (spec + to-do); each gets its own file.
