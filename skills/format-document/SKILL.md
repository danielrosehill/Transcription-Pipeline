---
name: format-document
description: Typeset a transcript or any of its reshaped versions as a PDF with Typst - a clean A4 document from Markdown, or a conversation layout with speech bubbles per speaker, title, summary and decisions (calls, meetings, interviews). Use on "make it a PDF", "nice document", "with speech bubbles", "something I can send".
---

# Format as a document

Needs `typst` (https://typst.app, single binary). Templates in `${CLAUDE_PLUGIN_ROOT}/templates/typst/`.
Compile with `--root /` so templates can read files anywhere.

## Markdown -> PDF

```bash
typst compile --root / --input md=<abs path to .md> --input title="<title>" --input date="<YYYY-MM-DD>" \
  ${CLAUDE_PLUGIN_ROOT}/templates/typst/document.typ <stem>.pdf
```
Uses the `cmarker` Typst package (downloaded once on first compile).

## Conversation with speech bubbles

Build a JSON file from the labelled transcript, then compile:
```json
{"title": "Family meeting", "subtitle": "Discussing vacation plans", "date": "2026-11-02",
 "participants": ["Daniel", "Hannah"], "summary": "Optional short paragraph.",
 "decisions": ["Optional", "list"], "turns": [{"speaker": "Daniel", "text": "..."}, {"speaker": "Hannah", "text": "..."}]}
```
```bash
typst compile --root / --input data=<abs path to turns.json> ${CLAUDE_PLUGIN_ROOT}/templates/typst/conversation.typ <stem>.pdf
```
Speakers alternate sides and colours in `participants` order. Use the cleaned (not raw) text in the bubbles unless
the user wants verbatim. For a short version ("just the minutes, as a PDF") put the minutes in `summary`/`decisions`
and leave `turns` empty, or use `document.typ` on the minutes file.

Check the PDF renders (convert page 1 to PNG and look at it) before handing it over. Custom layouts: copy a template
to `<prefs>/typst/` and edit there.
