---
name: batch-pipeline
description: Run the transcription pipeline over several recordings at once - the same process for each file, run concurrently, one worker per file (or per small batch). Use on "transcribe these three files", "do the same for all the voice notes in this folder", "batch these calls into minutes", or any request that names more than one recording.
---

# Run the pipeline over many recordings

A wrapper around `run-pipeline`. The files are independent, so they run at the same time. Every per-file rule
in `run-pipeline` still holds (keep every artefact, never overwrite, report cost).

## 1. Settle the shared decisions once

Before anything runs, work out from the request and the preferences the settings every file shares: source,
preprocessing, backend/model, cleanup level, speaker labels, reshape template(s), format, save target. Say them
in one line. Ask only if one file clearly needs something different (one long multi-speaker call among short
memos: give that file `assemblyai` and say so). Do not ask once per file.

List the input files with their durations (`ffprobe`) and the output stem each one will get. Two inputs with the
same stem get `-2`, `-3` so their outputs cannot collide.

## 2. Split the work

| Files | Split |
|---|---|
| 1 | not a batch: use `run-pipeline` |
| 2-8 | one worker per file |
| 9+ | batches of about 4 files per worker; keep long recordings (> 30 min) in their own worker |

Run at most 8 workers at once. Start the rest as earlier ones finish.

## 3. Run the workers

**Agents that can start subagents (Claude Code: the Agent tool):** start every worker in **one message**, so they
run in parallel. Each worker gets a self-contained brief:

- the file path(s) and output stem(s);
- the settled settings from step 1, written out in full (the worker has not seen the conversation);
- "Follow `${CLAUDE_PLUGIN_ROOT}/skills/run-pipeline/SKILL.md` and the stage skills it names, for these files only.
  Do not ask the user questions; if something blocks you, stop and report it.";
- the reply to send back: one JSON object per file:
  `{"input": ..., "outputs": [paths or links], "backend": ..., "model": ..., "cost_usd": ..., "status": "ok" | "failed", "error": ...}`.

Workers save their own outputs. Workers must not write to a shared file (one README index, one combined
document): the orchestrator does that in step 4.

**Agents without subagents:** run the expensive, waiting-heavy steps concurrently from the shell, then do the
text steps yourself one file at a time:

```bash
for f in a.m4a b.m4a c.m4a; do
  ( uv run --script scripts/preprocess.py "$f" --vad conservative > "${f%.*}.prep.json" ) &
done; wait
# then transcribe.py on each .prep file the same way (background + wait), then clean/reshape per file
```

## 4. Collect

- Read every worker's JSON. Check each listed output exists and is not empty; re-run a failed file once on its
  own before reporting it as failed.
- Do the shared steps now, if any were asked for: one index (README links, a combined summary across files, one
  email or Drive folder link for the set).
- Report one table: file, outputs, backend/model, cost, status. Then the total cost. No step-by-step recap.
