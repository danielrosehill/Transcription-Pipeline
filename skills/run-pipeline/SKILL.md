---
name: run-pipeline
description: Transcribe a recording end to end - fetch it, prepare it, transcribe it, clean it up, reshape it (spec, minutes, to-do, blog...), format it (PDF) and save every artefact where it belongs. The entry point for "transcribe this", "I just recorded a voice note about X", "turn this call into minutes and put it on Drive", or a named output set from the user's preferences.
---

# Run the transcription pipeline

Stages, in order. Each is its own skill; this one decides which run and with what settings.

```
retrieve-audio -> preprocess-audio -> transcribe-audio -> clean-transcript -> label-speakers -> reshape-transcript -> format-document -> save-outputs
   (collect)         (EQ/denoise,        (ASR backend)       (light/heavy)      (diarized only)     (spec, minutes,      (PDF)              (repo, folder,
                     downsample, VAD)                                                               to-do, blog...)                         Drive, bucket)
```

## Before starting

1. Read the user's preferences (see the `setup` skill for the path). If there is none, use the defaults below
   and offer `setup` once at the end, not before.
2. Work out from the request: the source, the backend, which outputs, and where they go. If the user named an
   output set ("call", "dev-brief"), use its recipe. Ask only when a choice changes cost a lot or where things are
   published; otherwise choose and say which way in one line.

## Defaults

| Decision | Default | Switch when |
|---|---|---|
| Preprocess | downsample + conservative silence trim; EQ and denoise per preferences (off if unset) | file already small mono speech: skip; very noisy: add denoise |
| Backend | `openrouter`, `~google/gemini-flash-latest`, prompt `raw` | > 20 min, timestamps, or several speakers: `assemblyai`; user names a model/slot/server |
| Cleanup | `light`, done by the agent itself | user asks for headings / restructure / ASR fixes: `heavy`; user names a model: `scripts/rewrite.py` |
| Reshape | none | the request implies one (spec, minutes, to-do, email, summary, blog) |
| Format | Markdown | user asks for a PDF or document |
| Save | next to the source, or the current repo's `idea/` or `transcripts/` folder | preferences or request name a target |

## Rules that hold in every run

- **Keep every artefact.** Text is cheap. Never replace the raw transcript with the cleaned one, or the cleaned one
  with a reshape. Naming: `<stem>.raw.txt`, `<stem>.raw.srt`, `<stem>.clean.md`, `<stem>.<template>.md`, `<stem>.pdf`,
  plus `<stem>.meta.json` from the ASR step.
- **Never overwrite** the source recording or an existing output; add `-2`, `-3`.
- **Cost:** transcription is cheap (cents per hour on Flash, about $0.15-0.40/h on AssemblyAI). Do not ask before
  running it. Report the cost the ASR step printed.
- **The recording itself** goes into a repo or shared folder only if the user says so (see `save-outputs`).
- At the end, list the files written (paths or links) and the cost. No recap of the steps.

## Example recipes

- *Voice note about software to build, in a repo:* local/Drive file -> preprocess -> openrouter raw -> clean light ->
  reshape `dev-spec` -> save to `./idea/` (raw, clean, spec; ask about including the recording).
- *Long family or business call:* preprocess -> assemblyai with speakers -> label-speakers (names from the user or
  preferences) -> clean light -> reshape `minutes` -> PDF `conversation` -> save raw + PDF + downsampled audio to the
  Drive target -> send the link if asked. Keeping the original audio and raw transcript next to the final document
  is the audit trail if anyone later disputes what was said.
