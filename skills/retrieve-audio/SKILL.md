---
name: retrieve-audio
description: Collect the recording to transcribe - the newest file in a Google Drive folder the user named, a local folder or path, an S3/MinIO/Wasabi/R2 bucket, or a URL (including YouTube). Also gets a local file to where the transcription will run when the agent's tools live on another machine (staging). First stage of the pipeline.
---

# Retrieve audio

Read the user's preferences first: the **Sources** table maps names ("my dev-plans folder", "the desktop one")
to locations, and says how this environment reaches Drive and S3. Assume that access is already set up;
this plugin ships no Drive or S3 client of its own.

Pick the reference for the source kind and follow it:

| Source | Reference |
|---|---|
| A path, or a named local folder | `references/local.md` |
| Google Drive folder or file link | `references/google-drive.md` |
| S3-compatible bucket (AWS S3, MinIO, Wasabi, R2, B2) | `references/s3.md` |
| http(s) URL, YouTube or other video site | `references/url.md` |

"The latest", "the one I just recorded", "it's in the folder": take the newest audio file by modified time. If
several arrived in the last few minutes and the request does not say which, list them (name, duration, time) and ask.

Work in a per-recording folder (the current repo if the recording is about it, else next to the source or a temp
folder) and never modify the source file.

## When the file and the tools are on different machines

If transcription will run somewhere that cannot read the user's disk (tools on a remote gateway or server, a
cloud agent), the audio has to travel. Options, best first:

1. Run `scripts/transcribe.py` on the machine that has the file; only the API call leaves it. Usually possible.
2. Stage it: upload to a bucket and pass a short-lived presigned URL (AssemblyAI takes URLs directly; the
   script downloads URLs itself for other backends). The user's preferences say which bucket and command;
   use a bucket with an expiry policy and delete the object after use.
3. Inline base64 through a tool call. Last resort: large payloads waste context and fail on long recordings.
