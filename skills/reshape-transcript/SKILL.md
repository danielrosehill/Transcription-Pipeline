---
name: reshape-transcript
description: Rewrite a cleaned transcript into another document type - development spec or brief, notes, summary, meeting minutes, to-do list, email, blog outline, blog post, or any format the user describes or has saved as a template. Keeps the transcript files and adds the new one. Use on "turn this into a spec", "make minutes", "pull out the to-dos", "write it up as a blog post", or any "turn this into X".
---

# Reshape a transcript

Input: normally `<stem>.clean.md` (fall back to the raw one). Output: `<stem>.<suffix>.md`, alongside the others.

## Templates

Look in this order, first match wins:
1. `<prefs>/templates/<name>.md` (the user's own; path in the `setup` skill)
2. `${CLAUDE_PLUGIN_ROOT}/templates/reshape/<name>.md`: the core set, written for transcripts:
   `dev-spec` (suffix `spec`), `notes`, `summary`, `minutes`, `todo`, `email`, `blog-outline`, `blog-post`.
3. `${CLAUDE_PLUGIN_ROOT}/templates/library/`: 206 text-transformation prompts in 14 categories (cover letter,
   SOP, SITREP, BLUF email, calendar entries as `.ics`, CSV/YAML/JSON, Hebrew email, tone shifts...). Search
   `templates/library/index.json` (`slug`, `name`, `category`, `output`, `summary`); open only the chosen
   `<category>/<slug>.md`. Output suffix = the slug unless the user names one; extension follows `output`
   (`json` -> `.json`, `ics` -> `.ics`, otherwise `.md`).

The user can also hand you a prompt of their own (pasted, or a file path): use it as is.

Nothing fits? Write the instruction from the request ("one-page brief for my accountant, formal") and use it as
the prompt. If the user is likely to ask for it again, offer to save it to `<prefs>/templates/`; the same goes
for a library prompt they keep choosing.

"What formats are there?": list the core set and the library categories with counts from `index.json`, not
all 206 prompts.

## Executor

- **Agent (default):** apply the template to the transcript yourself.
- **External model** if named: `scripts/rewrite.py <input> --prompt <template> -o <output> [--model ...] [--extra "..."]`.

## Rules

- Never invent content; everything in the output must trace back to the transcript. Gaps go in an "Open questions"
  or "To research" section, not into the text.
- Spoken order is not document order: put things where they belong (a dev spec follows build order).
- When the speaker contradicted themselves, keep the later statement and flag the contradiction.
- These rules override any template, including library prompts that tell the model to infer names or details.
- Several reshapes from one transcript are fine (spec + to-do); each gets its own file.
