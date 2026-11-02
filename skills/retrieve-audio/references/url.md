# URLs and video sites

**Direct audio URL** (presigned, public file): pass it straight to `scripts/transcribe.py`. AssemblyAI fetches it
server-side; other backends download it first.

**YouTube and other sites:** download audio only with yt-dlp.
```bash
yt-dlp -x --audio-format mp3 --audio-quality 5 -o "%(title)s.%(ext)s" "<url>"
```
If YouTube refuses ("This video is not available", signature errors), newer yt-dlp needs a JS runtime:
`--js-runtimes node:$(which node) --remote-components ejs:github`. Update yt-dlp before debugging further.
Respect the content's terms; this is for the user's own or permitted material.
