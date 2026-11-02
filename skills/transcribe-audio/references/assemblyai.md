# AssemblyAI

- Key `ASSEMBLYAI_API_KEY` (header `authorization: <key>`, no "Bearer"). EU data residency: host `api.eu.assemblyai.com`.
- Flow: `POST /v2/upload` (raw bytes) -> `upload_url`, or skip upload and pass any reachable URL; `POST /v2/transcript`
  with `audio_url`, `speech_models: ["universal"]`, `language_detection` or `language_code`, and
  `speaker_labels` / `speakers_expected` for diarization; poll `GET /v2/transcript/{id}` every 5 s;
  `GET /v2/transcript/{id}/srt` for subtitles.
- The script writes the SRT every time (free), and, when speakers were labelled, a raw text of
  `Speaker A: ...` turns. Real names come later in `label-speakers`.
- Good for: long-form (an hour is routine), timestamps, diarization. Price in the order of $0.15-0.40 per audio hour
  depending on model and features; check the current price before a large batch.
- 2026-11-02: `universal` resolved to `universal-2`.
