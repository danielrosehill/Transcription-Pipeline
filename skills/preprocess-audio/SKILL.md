---
name: preprocess-audio
description: Prepare a recording before transcription - optional denoise (FFT or DeepFilterNet for very noisy audio), optional speech EQ (shipped presets or the user's own), conservative silence trimming, and downsampling to mono 16 kHz in a small codec. Smaller uploads, lower cost, cleaner input. Use before any ASR backend, or on "clean up this audio first", "it's noisy", "too big to upload".
---

# Preprocess audio

One script, `${CLAUDE_PLUGIN_ROOT}/scripts/preprocess.py` (needs `ffmpeg`, `uv`). Writes a new file, never
touches the input, prints a JSON report (before/after duration and size, what was applied).

```bash
uv run --script ${CLAUDE_PLUGIN_ROOT}/scripts/preprocess.py <input> [--preset asr|gemini|local|archive] \
  [--vad off|conservative|moderate|aggressive] [--eq none|default|phone|headset|<preset.json>] \
  [--denoise none|afftdn|arnndn|deepfilter] [-o <output>]
```

Chain order: denoise -> EQ/dynamics -> silence trim -> mono, resample, encode.

## Choosing settings

Read the **Preprocessing** section of the user's preferences first; it sets their EQ preset and denoise default.

| Setting | Default | Notes |
|---|---|---|
| `--preset` | `asr`: mono 16 kHz MP3 32 kbps | accepted by every backend. `gemini`: Opus 24 kbps OGG, smallest (Gemini, OpenRouter, AssemblyAI; **not** OpenAI's API). `local`: 16 kHz WAV for whisper.cpp/Parakeet. `archive`: 48 kbps MP3 for a copy people will listen to. |
| `--vad` | `conservative`: gaps of 6 s+ become 0.5 s | over-trimming loses context and clips quiet words, so stay conservative unless the user asks. `moderate` 3 s, `aggressive` 2 s -> 0.3 s. |
| `--eq` | `none` unless preferences set one | shipped: `default` (rumble cut, -2 dB at 250 Hz, +2 dB at 3 kHz, light compression), `phone`, `headset`. A user preset is a JSON file in their preferences folder. EQ helps most on boomy or muffled recordings; for clean speech the gain to ASR is small. |
| `--denoise` | `none` | only for genuinely noisy audio (traffic, fans, crowd, a crying baby). `afftdn` is built into ffmpeg; `deepfilter` (DeepFilterNet) is much stronger but needs its binary; `arnndn` needs an RNNoise model file. Denoising clean speech can hurt accuracy, so do not apply it by default. |

Skip preprocessing when the file is already small mono speech at a low bit rate, or the user wants the
untouched original sent.

Report: duration trimmed, size before -> after, and which EQ/denoise ran.
