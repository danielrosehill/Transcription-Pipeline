# Transcription Pipeline

Agent skills for turning recordings into usable text, in stages:

```
retrieve -> preprocess -> transcribe -> clean -> label speakers -> reshape -> format -> save
```

Collect a voice note from a Google Drive folder, a local folder, a bucket or a URL. Prepare it with EQ, optional
denoise, conservative silence trimming and downsampling. Transcribe it with OpenRouter (latest Gemini Flash by
default), AssemblyAI, Gemini or your own Whisper/Parakeet server. Clean it up, name the speakers, and turn it into a
spec, minutes, a to-do list or a blog post. Typeset it as a PDF and save every artefact where it belongs.

Works as a Claude Code plugin and as plain skills for any agent that reads `SKILL.md` files.

## Install

Claude Code:

```
/plugin marketplace add danielrosehill/Claude-Code-Plugins
/plugin install transcription-pipeline@danielrosehill
```

Then say "set up transcription". The `setup` skill writes your preferences and checks your keys.

Requirements: `ffmpeg`, [`uv`](https://docs.astral.sh/uv/), and at least one of these keys: `OPENROUTER_API_KEY`,
`ASSEMBLYAI_API_KEY`, `GEMINI_API_KEY`. You can also use a local ASR server instead of a key. `typst` is needed
for PDFs and `yt-dlp` for video URLs.

## Skills

| Stage | Skill | What it does |
|---|---|---|
| | `run-pipeline` | Entry point. Runs the stages below with sensible defaults or one of your named recipes. |
| | `setup` | Writes your preferences file: sources, keys, model slots, servers, EQ, save targets. |
| 1 | `retrieve-audio` | Fetches the newest recording from local folders, Google Drive, S3/MinIO/Wasabi/R2 or a URL. Stages the file when your tools run on another machine. |
| 2 | `preprocess-audio` | Optional denoise (FFT or DeepFilterNet), EQ presets, 6 s+ silence trimming, and mono 16 kHz in MP3 or Opus. |
| 3 | `transcribe-audio` | Sends the audio to OpenRouter, AssemblyAI, Gemini or a local OpenAI-compatible server, and saves the output untouched. |
| 4 | `clean-transcript` | Light cleanup (disfluencies, self-corrections, paragraphs) or heavy (adds headings and de-duplication, and fixes ASR errors with inline markers). |
| 4 | `label-speakers` | Turns Speaker A/B into real names, worked out from content, from voice descriptions, or from clips you listen to. |
| 4 | `reshape-transcript` | Rewrites the transcript as a dev spec, notes, summary, minutes, to-do list, email, blog outline or post, or a template of your own. |
| 5 | `format-document` | Typst PDF: either a clean document or a conversation layout with speech bubbles. |
| 6 | `save-outputs` | Saves to the repo, a folder, Drive or a bucket. Includes the recording only if you ask, and can add an "Original idea recording" README link. |

Every run keeps all its artefacts: `<stem>.raw.txt` and `.raw.srt` from the ASR, `.clean.md`, and `.<template>.md`
for each reshape, `.pdf`, and `.meta.json` (the model actually used, the time taken and the cost). Nothing is ever
overwritten.

## Your preferences stay out of the plugin

The plugin ships generic. Your Drive folder links, model favourites (`or1`, `or2`...), home ASR server, EQ preset,
speaker names and save targets live in one Markdown file:
`~/.claude-user-data/transcription-pipeline/preferences.md`. You can move it with `$TRANSCRIPTION_PREFS_DIR` or
`$CLAUDE_USER_DATA`. The template is [`templates/preferences.example.md`](templates/preferences.example.md).

The file is plain Markdown, so any agent can use it and you can edit it by hand. Updating the plugin never
conflicts with your own setup, because the agent never rewrites the plugin's skills to fit you. Your own EQ
presets, reshape templates and Typst layouts go in the same folder, and they take precedence over the shipped ones.

## Scripts

All three scripts are uv single-file scripts that print JSON:

```bash
uv run --script scripts/preprocess.py memo.m4a --eq default --vad conservative
uv run --script scripts/transcribe.py memo.prep.mp3                       # OpenRouter, ~google/gemini-flash-latest, verbatim
uv run --script scripts/transcribe.py call.mp3 --backend assemblyai --speakers 2
uv run --script scripts/transcribe.py memo.wav --backend local --local-url http://localhost:8000 --model <id>
uv run --script scripts/rewrite.py memo.raw.txt --prompt templates/prompts/cleanup-light.md -o memo.clean.md
```

## Original idea recording

This plugin was specified in a voice note:
[2026-11-02_transcription-plugin-voice-note.mp3](idea/2026-11-02_transcription-plugin-voice-note.mp3) (22:12,
recorded 2026-11-02). It was transcribed with this pipeline:
[raw](idea/2026-11-02_transcription-plugin-voice-note.raw.txt) ·
[cleaned](idea/2026-11-02_transcription-plugin-voice-note.clean.md) ·
[spec](idea/2026-11-02_transcription-plugin-voice-note.spec.md)

## Lineage

This plugin succeeds and consolidates `Claude-Transcription-Plugin` (whose plugin name, `transcription-pipeline`,
it takes over), `Gemini-Transcription-MCP` (end of life), `OR-Audio-Transcription-MCP`, `Cloud-ASR-MCP`, and a
private router plugin. See [docs/prior-art.md](docs/prior-art.md) for what was carried over, what was dropped,
and why it no longer uses MCP servers.

## License

MIT
