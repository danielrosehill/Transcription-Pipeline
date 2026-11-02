---
name: save-outputs
description: Put the finished transcription artefacts where they belong - the current repo, a local folder, a Google Drive folder (with per-type subfolders), or a bucket - with consistent names, the recording itself only when the user wants it, and, in a repo, an optional "Original idea recording" link in the README. Final stage of the pipeline; also on "save this to Drive", "put it in the repo", "keep the audio with it".
---

# Save outputs

## Names

`<stem>` is `YYYY-MM-DD_<short-slug>` unless the user or the source file already gave a good name. Every artefact
keeps its role suffix: `.raw.txt`, `.raw.srt`, `.meta.json`, `.clean.md`, `.labelled.md`, `.<template>.md`, `.pdf`,
and the audio as `<stem>.<ext>`. Never overwrite; add `-2`.

## Targets

Read **Save targets** in preferences. Without one:
- inside a git repo and the recording is about it: `./idea/` for the recording and its transcripts (or an existing
  `transcripts/` folder);
- otherwise next to the source file.

Google Drive and buckets: upload with the access the preferences name (MCP, rclone, CLI). Use the subfolder for
the output type if the preferences define one (calls, dev plans...). Return links, not just names.

## The recording itself

Whether the audio goes with the transcripts is the user's call each time, unless preferences say `yes` or `no`.
Ask once, plainly: "Include the recording in <target>?" Do not assume they want it kept private just because the
target is a public repo: many people deliberately publish the original recording as a record of their thinking.

When it is included:
- Save the **processed** version, not the raw capture: `preprocess.py --preset archive --vad conservative`
  (mono 48 kbps MP3, roughly 20 MB per hour) so it is listenable and small.
- Over ~50 MB, warn: GitHub blocks files over 100 MB and the file stays in git history; offer Git LFS, a release
  asset, or Drive with a link instead.
- In a repo, add (or update) a README section linking to the file:

  ```markdown
  ## Original idea recording

  This project started as a voice note: [<stem>.mp3](idea/<stem>.mp3) (<mm:ss>, recorded <date>).
  Transcript: [raw](idea/<stem>.raw.txt) · [cleaned](idea/<stem>.clean.md) · [spec](idea/<stem>.spec.md)
  ```

## Audit bundle

For calls, meetings and anything that may be disputed later, save alongside the final document: the downsampled
recording, the raw transcript and the meta file. The final document is what people read; the raw pair is the
evidence of what was actually said.

## Then

- Delete staged copies in transient buckets; trash (never permanently delete) processed files in an inbox folder
  if the preferences say the inbox is emptied.
- Commit in a repo when the user's workflow commits (stage only the files written).
- If asked to notify someone ("email us the link"), do it with whatever mail tool the environment has.
