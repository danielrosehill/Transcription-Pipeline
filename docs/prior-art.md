# Prior art and what this plugin replaces

Compiled 2026-11-02 from the repos below (read directly). This plugin is the **current** line; everything listed is
superseded by it and marked so in its own README.

| Repo | Kind | Status | Carried over | Dropped, and why |
|---|---|---|---|---|
| `danielrosehill/Claude-Transcription-Plugin` | public plugin `transcription-pipeline` 2.2.1, 29 skills | superseded; marketplace entry now points here | ffmpeg presets (16 kHz mono, Opus 24k / MP3 32k), Gemini raw/clean prompts, YouTube download, Typst PDF layout, speaker-sample extraction idea, output naming that never overwrites | its MCP dependency (`gemini-transcription`); `config.json` provider schema (replaced by a readable preferences file); 29 narrow skills (folded into 10 stage skills); translate, combine-versions, split-transcript, messy-audio-fix (rarely used; any agent can do them ad hoc) |
| `danielrosehill/Transcription-Router-Plugin` (private) | private plugin, single router script | superseded | one script with JSON on stdout, `<stem>` sidecar with cost/elapsed, cleanup and reshape templates (cleaned, dev-prompt, notes, summary, minutes, todo, email, blog), long-file chunking at 40 min, "latest Flash" by default | personal backends (home server, desktop) move to the user's preferences as `local` servers; on-device sherpa-onnx path not ported |
| `danielrosehill/Gemini-Transcription-MCP` | public MCP | end of life | verbatim-with-minimal-cleanup prompt rules (spelled-out words, trailing off, "scratch that"), dev-spec section list | MCP transport, base64-over-tool-call upload (wastes context and failed on long files), JSON-wrapped responses |
| `danielrosehill/OR-Audio-Transcription-MCP` | public MCP | superseded | OpenRouter `input_audio` call shape | MCP; `audio_url` fallback (not needed) |
| `danielrosehill/Cloud-ASR-MCP` | public WIP MCP | superseded | Gemini Files API upload-poll-delete flow | MCP; OpenAI and Mistral direct backends (both reachable through OpenRouter) |
| `danielrosehill/Long-Form-Audio-Pipeline` | scripts | reference | speech EQ chain idea, compression data point (47 min WAV 483 MB -> 17 MB Opus) | unvalidated EQ values |
| `danielrosehill/audacity-transcription-presets` | presets/docs | reference | container trap (OpenAI's API rejects .ogg/.opus/.flac), "do not re-encode lossy to lower lossy" | Audacity-specific macros |
| `danielrosehill/Diarised-Transcript-Assistant` | prompt | reference | naming speakers from voice descriptions plus content | the single-pass audio-in format (diarization now comes from AssemblyAI labels + `label-speakers`) |
| HF `danielrosehill/Text-Transformation-Prompts-300525` | prompt dataset, 206 prompts | frozen; vendored | all 206 prompts, unchanged text, as `templates/library/` with categories and an index | the HF dependency; the per-prompt JSON duplicates |
| `danielrosehill/Audio-Multimodal-Formatting-Prompts` | prompt library | reference | none directly; a seed corpus for user templates | generated prompts of uneven quality |

## Why no MCP servers

The MCP servers existed to give agents a transcription tool. In practice a plugin that ships a script and says
"call the API with the key in the environment" does the same with less to run. The servers also forced audio
through tool calls as base64, which bloated context and failed on long recordings, and they ran on whichever
machine hosted the server, which often could not see the user's files (the reason for the staging-bucket
workaround, still documented in `retrieve-audio`).

## Evidence notes
- No repo measured whether EQ or bit rate changes accuracy. The EQ presets are for clarity and are off by default.
- Denoise: an earlier test (DeepFilterNet vs raw, 119 s of speech over a crying baby) differed by 5-6 words,
  so denoise is opt-in for genuinely noisy audio only.
- Silero-based gap capping (0.4 s) removed 13.9% of a 42-minute memo without clipping words in an earlier
  plugin; this plugin's default is far more conservative (6 s gaps -> 0.5 s) at the voice note's request.
