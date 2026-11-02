---
name: setup
description: First-time setup and later changes to how transcription works for this user. Writes a plain preferences file (sources such as Google Drive folders, keys, default backend, OpenRouter model slots, local ASR servers, EQ preset, save targets, named output sets) and checks the API keys work. Use on "set up transcription", "add my Drive folder", "change my default model", "is transcription working?".
---

# Set up transcription preferences

The plugin ships generic. Everything specific to this user lives in one Markdown file in their
preferences folder, which every other skill reads before acting. Do not edit the plugin's own
files to fit the user: that forks it and breaks updates.

**Preferences folder:** `$TRANSCRIPTION_PREFS_DIR`, else `$CLAUDE_USER_DATA/transcription-pipeline/`, else `~/.claude-user-data/transcription-pipeline/`. Call it `<prefs>` below. File: `<prefs>/preferences.md`.
Custom EQ presets go in `<prefs>/eq/`, custom reshape templates in `<prefs>/templates/`.

## First run

1. If `<prefs>/preferences.md` does not exist, copy `${CLAUDE_PLUGIN_ROOT}/templates/preferences.example.md` there.
2. Ask only what is needed now, in one message. Accept pasted links as-is:
   - Where recordings arrive (Drive folder links, local folders, buckets) and what each is for.
   - How this environment reaches Drive / S3 (an MCP, rclone, a CLI). Check what is actually available rather than asking when you can.
   - Which API keys exist (check the environment for `OPENROUTER_API_KEY`, `ASSEMBLYAI_API_KEY`, `GEMINI_API_KEY`; if the user's keys live under other names or behind a secrets runner, record that).
   - Where finished transcripts should go.
3. Fill the file. Turn a Drive folder link into its ID (the part after `/folders/`) but keep the link too.
4. Check the keys cheaply:
   - OpenRouter: `curl -s https://openrouter.ai/api/v1/auth/key -H "Authorization: Bearer $OPENROUTER_API_KEY"`
   - AssemblyAI: `curl -s "https://api.assemblyai.com/v2/transcript?limit=1" -H "authorization: $ASSEMBLYAI_API_KEY"`
   - Gemini: `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -c 200`
   - Local servers: `curl -s <url>/v1/models`
   - Tools: `ffmpeg -version`, `uv --version`, `typst --version` (PDF only), `yt-dlp --version` (URLs only).
   Report one line per item: works / missing / failed with the error.

## Later changes

Edit the matching section in place ("add a source", "make or2 the default", "my wife's name is ..."). Never
delete a section the user filled; mark retired entries instead.

## OpenRouter model slots

Slots (`or1`, `or2`, ...) let the user say "use or2" or "the cheap one". To refresh the list of audio-capable models:

```bash
curl -s https://openrouter.ai/api/v1/models | jq -r '.data[] | select(.architecture.input_modalities | index("audio")) | "\(.id)\t\(.pricing.audio // .pricing.prompt)"'
```

`~google/gemini-flash-latest` is a floating alias that follows new Gemini Flash releases; it can lag the newest numbered Flash by a release. Pin a numbered id when output must not change silently.

## EQ preset from the user's own voice (optional)

If the user wants an EQ fitted to their voice: take a typical recording, measure octave-band levels of speech
(`ffmpeg -af "bandpass=f=<fc>:width_type=o:w=1,volumedetect"` per band 125 Hz-8 kHz), cut bands that stand
more than 1 dB above the speaker's spectral trend and lift ones below, at 60% strength, capped at ±3 dB, and save as
`<prefs>/eq/<name>.json` in the preset format documented in `scripts/preprocess.py`. Then set it in the preferences.
