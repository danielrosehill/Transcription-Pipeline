# Gemini direct (Google AI Studio)

- Key `GEMINI_API_KEY` (or `GOOGLE_API_KEY`). Default model `gemini-flash-latest` (Google's own floating alias;
  2026-11-02 it resolved to `gemini-3.8-flash`).
- The script always uses the Files API (resumable upload, wait for `ACTIVE`, `generateContent` with `file_data`, then
  delete the file), so long recordings work; inline audio is limited to 20 MB per request.
- Audio costs about 32 tokens per second. Native formats: wav, mp3, aiff, aac, ogg, flac.
- Same prompts as OpenRouter (`--mode raw|light`, `--prompt-file`).
