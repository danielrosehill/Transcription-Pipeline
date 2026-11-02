# OpenRouter (default)

- Endpoint `POST https://openrouter.ai/api/v1/chat/completions`, key `OPENROUTER_API_KEY`.
- Audio goes in a user message as `{"type": "input_audio", "input_audio": {"data": <base64>, "format": "mp3"}}`
  next to a text part carrying the prompt. Formats: wav, mp3, ogg, flac, aac, aiff, m4a; the script converts others.
- Default model `~google/gemini-flash-latest`: a floating alias that moves to new Gemini Flash releases, so
  the default never needs editing. The meta file records the model it actually resolved to
  (2026-11-02: `google/gemini-3.8-flash`). Pin a numbered id when output must stay comparable over time.
- Cost is returned per call (`usage.cost`) and written to meta. 2026-11-02: a 30 s clip cost $0.004.
- Long recordings: the whole file travels as base64 in one JSON body. The script splits anything over 40 minutes
  into 40-minute pieces and joins the text; above ~20 MB it warns. Preprocess first (32 kbps mono keeps an hour
  around 14 MB).
- Other audio-capable models (check the live list with the `setup` skill command): Gemini Flash Lite (cheapest),
  Gemini Pro, Voxtral, Qwen omni, MiMo, OpenAI gpt-audio. Keep the user's favourites as slots in preferences.
