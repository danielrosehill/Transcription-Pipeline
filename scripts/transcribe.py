#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""Send one audio file (or URL) to one ASR backend and save what comes back, untouched.

Backends (keys come from the environment; nothing is read from config files here):
  openrouter  OPENROUTER_API_KEY   audio-capable chat model, default ~google/gemini-flash-latest
  assemblyai  ASSEMBLYAI_API_KEY   long-form, timestamps (SRT), speaker labels
  gemini      GEMINI_API_KEY       Google AI Studio direct, Files API upload (long files), default gemini-flash-latest
  local       (none, or LOCAL_ASR_API_KEY)  any OpenAI-compatible /v1/audio/transcriptions server
              (whisper.cpp server, faster-whisper-server/speaches, a Parakeet gateway...)

Writes into --out-dir (default: next to the input):
  <stem>.raw.txt    the transcript exactly as returned (always)
  <stem>.raw.srt    subtitles, when the backend gives timestamps (assemblyai; local with verbose_json)
  <stem>.raw.json   the provider's full response
  <stem>.meta.json  backend, model, prompt mode, timings, cost where reported
Prints the meta JSON to stdout.

    uv run --script transcribe.py memo.mp3
    uv run --script transcribe.py memo.mp3 --backend openrouter --model google/gemini-3.8-flash --mode light
    uv run --script transcribe.py call.mp3 --backend assemblyai --speakers 2
    uv run --script transcribe.py https://bucket/presigned.mp3 --backend assemblyai
    uv run --script transcribe.py memo.wav --backend local --local-url http://localhost:8080 --model whisper-1
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
PROMPTS = HERE.parent / "templates" / "prompts"
DEFAULT_MODEL = {
    "openrouter": "~google/gemini-flash-latest",
    "gemini": "gemini-flash-latest",
    "assemblyai": "universal",
    "local": "whisper-1",
}
# Above this, base64-in-JSON uploads (OpenRouter) get slow and fail more often. Preprocess first,
# or use gemini (Files API) / assemblyai (upload or URL) for long recordings.
INLINE_WARN_BYTES = 20 * 1024 * 1024
OPENROUTER_FORMATS = {"wav", "mp3", "ogg", "flac", "aac", "aiff", "m4a"}
TIMEOUT = httpx.Timeout(connect=30, read=900, write=900, pool=30)


def die(msg: str, **extra) -> None:
    print(json.dumps({"error": msg, **extra}, indent=2))
    sys.exit(1)


def env(name: str, *alts: str) -> str:
    for n in (name, *alts):
        if os.environ.get(n):
            return os.environ[n]
    die(f"missing API key: set {name}" + (f" (or {', '.join(alts)})" if alts else ""))


def load_prompt(mode: str, prompt_file: Path | None) -> str:
    if prompt_file:
        return prompt_file.read_text()
    f = PROMPTS / f"transcribe-{mode}.md"
    if not f.is_file():
        die(f"no prompt for mode '{mode}' at {f}")
    return f.read_text()


def materialise(src: str, workdir: Path) -> Path:
    """Local path stays as is; an http(s) URL is downloaded (for backends that need bytes)."""
    if not src.startswith(("http://", "https://")):
        p = Path(src).expanduser()
        if not p.is_file():
            die(f"no such file: {p}")
        return p
    name = Path(httpx.URL(src).path).name or "audio"
    dest = workdir / name
    with httpx.stream("GET", src, follow_redirects=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return dest


def to_supported(path: Path, allowed: set[str], workdir: Path) -> Path:
    ext = path.suffix.lower().lstrip(".")
    if ext in allowed:
        return path
    if not shutil.which("ffmpeg"):
        die(f".{ext} is not accepted by this backend and ffmpeg is not available to convert it")
    out = workdir / f"{path.stem}.mp3"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-vn", "-ac", "1",
                    "-ar", "16000", "-c:a", "libmp3lame", "-b:a", "32k", str(out)], check=True)
    return out


# --------------------------------------------------------------------------- backends

def duration(path: Path) -> float:
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                     "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip())
    except (ValueError, FileNotFoundError):
        return 0.0


def run_openrouter(src: str, model: str, prompt: str, workdir: Path, chunk_s: int = 2400, **_) -> dict:
    """Long recordings are split into chunk_s pieces (default 40 min, ~10 MB at 32 kbps) and joined."""
    path = to_supported(materialise(src, workdir), OPENROUTER_FORMATS, workdir)
    dur = duration(path)
    if dur <= chunk_s or not shutil.which("ffmpeg"):
        return openrouter_one(path, model, prompt)
    seg_dir = workdir / "chunks"
    seg_dir.mkdir()
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-f", "segment",
                    "-segment_time", str(chunk_s), "-c", "copy", str(seg_dir / f"part%03d{path.suffix}")], check=True)
    parts = [openrouter_one(c, model, prompt) for c in sorted(seg_dir.iterdir())]
    costs = [p["cost_usd"] for p in parts if p.get("cost_usd") is not None]
    return {"text": "\n\n".join(p["text"].strip() for p in parts), "raw": [p["raw"] for p in parts],
            "model_resolved": parts[0]["model_resolved"], "cost_usd": round(sum(costs), 6) if costs else None,
            "audio_duration_s": round(dur, 1), "chunks": len(parts)}


def openrouter_one(path: Path, model: str, prompt: str) -> dict:
    key = env("OPENROUTER_API_KEY")
    size = path.stat().st_size
    if size > INLINE_WARN_BYTES:
        print(f"warning: {size/1e6:.1f} MB inline upload; consider preprocess.py or --backend gemini/assemblyai",
              file=sys.stderr)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "input_audio", "input_audio": {
                "data": base64.b64encode(path.read_bytes()).decode(),
                "format": path.suffix.lower().lstrip(".")}},
        ]}],
        "temperature": 0,
        "usage": {"include": True},
    }
    r = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=body, timeout=TIMEOUT,
                   headers={"Authorization": f"Bearer {key}", "X-Title": "transcription-pipeline"})
    if r.status_code != 200:
        die("openrouter request failed", status=r.status_code, body=r.text[:2000])
    d = r.json()
    if "choices" not in d:
        die("openrouter returned no choices", body=json.dumps(d)[:2000])
    usage = d.get("usage") or {}
    return {"text": d["choices"][0]["message"]["content"] or "", "raw": d,
            "model_resolved": d.get("model"), "cost_usd": usage.get("cost")}


def run_gemini(src: str, model: str, prompt: str, workdir: Path, **_) -> dict:
    key = env("GEMINI_API_KEY", "GOOGLE_API_KEY")
    path = materialise(src, workdir)
    mime = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    base = "https://generativelanguage.googleapis.com"
    with httpx.Client(timeout=TIMEOUT) as c:
        # Files API resumable upload: handles long recordings that inline data cannot.
        start = c.post(f"{base}/upload/v1beta/files", params={"key": key},
                       headers={"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                                "X-Goog-Upload-Header-Content-Length": str(path.stat().st_size),
                                "X-Goog-Upload-Header-Content-Type": mime},
                       json={"file": {"display_name": path.name}})
        if start.status_code != 200:
            die("gemini upload start failed", status=start.status_code, body=start.text[:2000])
        up = c.post(start.headers["x-goog-upload-url"], content=path.read_bytes(),
                    headers={"X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"})
        f = up.json()["file"]
        for _ in range(60):
            if f.get("state") == "ACTIVE":
                break
            time.sleep(2)
            f = c.get(f"{base}/v1beta/{f['name']}", params={"key": key}).json()
        r = c.post(f"{base}/v1beta/models/{model}:generateContent", params={"key": key}, json={
            "contents": [{"parts": [{"text": prompt}, {"file_data": {"mime_type": mime, "file_uri": f["uri"]}}]}],
            "generationConfig": {"temperature": 0},
        })
        c.delete(f"{base}/v1beta/{f['name']}", params={"key": key})
    if r.status_code != 200:
        die("gemini request failed", status=r.status_code, body=r.text[:2000])
    d = r.json()
    parts = (d.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    return {"text": "".join(p.get("text", "") for p in parts), "raw": d, "model_resolved": d.get("modelVersion")}


def run_assemblyai(src: str, model: str, speakers: int | None, diarize: bool, language: str | None,
                   workdir: Path, **_) -> dict:
    key = env("ASSEMBLYAI_API_KEY", "ASSEMBLY_API_KEY")
    h = {"authorization": key}
    base = "https://api.assemblyai.com/v2"
    with httpx.Client(timeout=TIMEOUT, headers=h) as c:
        if src.startswith(("http://", "https://")):
            url = src  # AssemblyAI fetches it itself: no upload from this machine
        else:
            path = materialise(src, workdir)
            url = c.post(f"{base}/upload", content=path.read_bytes()).raise_for_status().json()["upload_url"]
        req = {"audio_url": url, "speech_models": [model], "punctuate": True, "format_text": True}
        if diarize or speakers:
            req["speaker_labels"] = True
            if speakers:
                req["speakers_expected"] = speakers
        if language:
            req["language_code"] = language
        else:
            req["language_detection"] = True
        job = c.post(f"{base}/transcript", json=req)
        if job.status_code != 200:
            die("assemblyai submit failed", status=job.status_code, body=job.text[:2000])
        tid = job.json()["id"]
        while True:
            d = c.get(f"{base}/transcript/{tid}").json()
            if d["status"] == "completed":
                break
            if d["status"] == "error":
                die("assemblyai transcription failed", detail=d.get("error"), id=tid)
            time.sleep(5)
        srt = c.get(f"{base}/transcript/{tid}/srt").text
    text = d.get("text") or ""
    if d.get("utterances"):
        text = "\n\n".join(f"Speaker {u['speaker']}: {u['text']}" for u in d["utterances"])
    return {"text": text, "raw": d, "srt": srt, "model_resolved": d.get("speech_model_used") or model,
            "audio_duration_s": d.get("audio_duration")}


def run_local(src: str, model: str, local_url: str | None, language: str | None, timestamps: bool,
              workdir: Path, **_) -> dict:
    base = (local_url or os.environ.get("LOCAL_ASR_URL") or "").rstrip("/")
    if not base:
        die("local backend needs --local-url or LOCAL_ASR_URL (an OpenAI-compatible server)")
    path = materialise(src, workdir)
    headers = {}
    if os.environ.get("LOCAL_ASR_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['LOCAL_ASR_API_KEY']}"
    data = {"model": model, "response_format": "verbose_json" if timestamps else "json"}
    if language:
        data["language"] = language
    with path.open("rb") as fh:
        r = httpx.post(f"{base}/v1/audio/transcriptions", data=data, headers=headers, timeout=TIMEOUT,
                       files={"file": (path.name, fh, mimetypes.guess_type(path.name)[0] or "application/octet-stream")})
    if r.status_code != 200:
        die("local ASR request failed", status=r.status_code, body=r.text[:2000], url=base)
    d = r.json()
    out = {"text": d.get("text", ""), "raw": d, "model_resolved": d.get("model") or model}
    if timestamps and d.get("segments"):
        out["srt"] = segments_to_srt(d["segments"])
    return out


def segments_to_srt(segs: list[dict]) -> str:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
    return "\n".join(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text'].strip()}\n"
                     for i, s in enumerate(segs, 1))


BACKENDS = {"openrouter": run_openrouter, "gemini": run_gemini, "assemblyai": run_assemblyai, "local": run_local}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="audio file path or http(s) URL")
    ap.add_argument("--backend", choices=BACKENDS, default="openrouter")
    ap.add_argument("--model", help="backend model id (defaults per backend, see --help)")
    ap.add_argument("--mode", default="raw", help="prompt for LLM backends: raw (verbatim) | light (no disfluencies)")
    ap.add_argument("--prompt-file", type=Path, help="custom transcription prompt (LLM backends)")
    ap.add_argument("--speakers", type=int, help="expected speaker count (assemblyai; implies --diarize)")
    ap.add_argument("--diarize", action="store_true", help="speaker labels (assemblyai)")
    ap.add_argument("--timestamps", action="store_true", help="ask local servers for segments -> .raw.srt")
    ap.add_argument("--language", help="ISO code, e.g. en, he (default: auto-detect where supported)")
    ap.add_argument("--local-url", help="base URL of an OpenAI-compatible ASR server (local backend)")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--stem", help="output file stem (default: input file stem)")
    a = ap.parse_args()

    model = a.model or DEFAULT_MODEL[a.backend]
    stem = a.stem or Path(httpx.URL(a.input).path if a.input.startswith("http") else a.input).stem
    stem = stem.removesuffix(".prep")
    out_dir = a.out_dir or (Path(a.input).expanduser().parent if not a.input.startswith("http") else Path.cwd())
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = load_prompt(a.mode, a.prompt_file) if a.backend in ("openrouter", "gemini") else None

    t0 = time.time()
    with tempfile.TemporaryDirectory() as td:
        res = BACKENDS[a.backend](src=a.input, model=model, prompt=prompt, speakers=a.speakers,
                                  diarize=a.diarize, language=a.language, local_url=a.local_url,
                                  timestamps=a.timestamps, workdir=Path(td))
    elapsed = round(time.time() - t0, 1)

    files = {"raw_txt": out_dir / f"{stem}.raw.txt", "raw_json": out_dir / f"{stem}.raw.json"}
    files["raw_txt"].write_text(res["text"].strip() + "\n")
    files["raw_json"].write_text(json.dumps(res["raw"], indent=2, ensure_ascii=False))
    if res.get("srt"):
        files["raw_srt"] = out_dir / f"{stem}.raw.srt"
        files["raw_srt"].write_text(res["srt"])
    meta = {
        "input": a.input, "backend": a.backend, "model_requested": model,
        "model_resolved": res.get("model_resolved"), "prompt_mode": None if prompt is None else
        (str(a.prompt_file) if a.prompt_file else a.mode),
        "elapsed_s": elapsed, "audio_duration_s": res.get("audio_duration_s"), "cost_usd": res.get("cost_usd"),
        "words": len(res["text"].split()), "chunks": res.get("chunks"), "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "files": {k: str(v) for k, v in files.items()},
    }
    files["meta"] = out_dir / f"{stem}.meta.json"
    meta["files"]["meta"] = str(files["meta"])
    files["meta"].write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
