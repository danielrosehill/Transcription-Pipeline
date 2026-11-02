# Changelog

## 3.1.0 (2026-11-02)

- New `batch-pipeline` skill: several recordings in one request. Settles the shared settings once, then runs one
  subagent per file (or per batch of about 4 when there are more than 8 files, at most 8 at once). Agents without
  subagents run preprocessing and transcription in the background from the shell. Ends with one results table and the total cost.
- New `templates/library/`: 206 text-transformation system prompts vendored from the frozen Hugging Face dataset
  `danielrosehill/Text-Transformation-Prompts-300525`, sorted into 14 categories with an `index.json` (slug, category,
  output format, summary). `reshape-transcript` uses it as its third template source, and still accepts a user's own prompt.

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
