# Changelog

## 3.0.0 (2026-11-02)

First release in this repository. Successor to `danielrosehill/Claude-Transcription-Plugin`
(plugin `transcription-pipeline` 2.2.1), which it replaces under the same plugin name.

- Rebuilt around six stages (retrieve, preprocess, transcribe, post-process, format, save), one skill each,
  plus `setup` and the `run-pipeline` orchestrator. 29 skills became 10.
- No MCP servers: the backends are called directly from `scripts/transcribe.py` with API keys from the environment.
- Preferences moved to one Markdown file (`~/.claude-user-data/transcription-pipeline/preferences.md` by default),
  readable by any agent, instead of `config.json`.
- Backends verified 2026-11-02: OpenRouter (`~google/gemini-flash-latest` -> gemini-3.8-flash), AssemblyAI
  (universal-2, SRT), Gemini direct (Files API), local OpenAI-compatible server (Parakeet).
- New: EQ presets and optional DeepFilterNet denoise in preprocessing; light/heavy cleanup with audited ASR fixes;
  speaker labelling by content, description or ear; Typst conversation PDF with speech bubbles; opt-in publishing
  of the recording with an "Original idea recording" README link.
