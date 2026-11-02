# Text transformation prompt library

206 system prompts that turn dictated or transcribed text into another form: emails, minutes, plans,
documentation, structured data, tone shifts, and some novelty styles. The `reshape-transcript` skill uses them
as its third template source, after the user's own templates and the shipped `templates/reshape/` set.

## Layout

- `index.json`: one entry per prompt: `slug`, `name`, `category`, `output` (`markdown`, `json`, `html`, `csv`,
  `yaml`, `toml`, `ics`, `sql`, `shell`), `path` (relative to this folder) and a one-line `summary`. Search this
  file; open a prompt only once you have chosen it.
- `<category>/<slug>.md`: the system prompt. Line 1 is a metadata comment, `<!-- name: ... | category: ... | output: ... -->`;
  the rest is the prompt. The transcript goes in as the user turn.

Categories: `ai-prompts`, `business-documents`, `career`, `cleanup-and-editing`, `documentation`,
`email-and-correspondence`, `humour-and-novelty`, `language`, `meetings`, `personal-and-journal`,
`planning-and-tasks`, `publishing-and-social`, `structured-data`, `tone-and-style`.

## Provenance

Copied on 2026-11-02 from the Hugging Face dataset `danielrosehill/Text-Transformation-Prompts-300525`
(`all_prompts.json`, last updated 2025-05-29, same author). That dataset is frozen, so this copy is the maintained
version and the plugin does not depend on Hugging Face. Changes made while copying it: each prompt was assigned a
category (keyword rules plus manual overrides), given a slug, and tagged with its output format (taken from the
prompt name or the dataset's `expected_output_format`), and spelling mistakes in seven names were fixed
(e.g. "Tempalte", "Profesesional"). The prompt text is unchanged.

The prompts were written for dictated notes, so a few ask the model to infer missing details. When they are used
on a transcript, the `reshape-transcript` rules take precedence: nothing is invented, and gaps are listed as open questions.
