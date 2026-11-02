# Local and self-hosted ASR

The `local` backend speaks the OpenAI transcription API: `POST <base>/v1/audio/transcriptions`, multipart `file`
and `model`, optional `language`, `response_format=verbose_json` for segments (-> `.raw.srt` with `--timestamps`).
Base URL from `--local-url`, `LOCAL_ASR_URL`, or the preferences' **Local / self-hosted ASR** table; bearer key
from `LOCAL_ASR_API_KEY` if the server wants one. List models with `curl <base>/v1/models`.

Servers that expose this API:
- **whisper.cpp** `whisper-server -m <model.bin> --port 8080` (the server's route is `/inference`; run it with
  `--inference-path /v1/audio/transcriptions` to match).
- **speaches / faster-whisper-server** (Whisper, distil-whisper): `docker run -p 8000:8000 ghcr.io/speaches-ai/speaches`.
- **NVIDIA Parakeet** behind any OpenAI-compatible wrapper (several community gateways; GGUF builds run on CPU).
- **LocalAI**, **vLLM** with Whisper.

No server, just a machine with Python: run faster-whisper directly and save the text as `<stem>.raw.txt` yourself:
```bash
uv run --with faster-whisper python -c "
from faster_whisper import WhisperModel; import sys
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe(sys.argv[1], beam_size=5, vad_filter=True)
print(' '.join(s.text.strip() for s in segs))" <file> > <stem>.raw.txt
```
Use the `local` preprocess preset (16 kHz WAV). Long files on small models: memory grows with length; chunk at
~10 minutes if a server does not chunk itself.
