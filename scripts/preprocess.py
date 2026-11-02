#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Prepare audio for ASR: downsample to mono at a sane rate, optionally trim long silences.

Needs ffmpeg/ffprobe on PATH. Never touches the input file; writes a new one and prints
a JSON report (input/output duration, size, what was applied) to stdout.

    uv run --script preprocess.py memo.wav                      # preset "asr": mono 16 kHz MP3 32 kbps + conservative VAD
    uv run --script preprocess.py memo.wav --preset gemini      # mono 16 kHz OGG/Opus 24 kbps
    uv run --script preprocess.py memo.wav --vad off            # downsample only
    uv run --script preprocess.py memo.wav --vad aggressive     # silences > 2 s collapse to 0.3 s
    uv run --script preprocess.py memo.wav --eq default         # shipped speech EQ (templates/eq/speech-default.json)
    uv run --script preprocess.py memo.wav --eq ~/my-voice.json # the user's own preset
    uv run --script preprocess.py memo.wav --denoise afftdn     # light FFT denoise (built into ffmpeg)
    uv run --script preprocess.py memo.wav --denoise deepfilter # DeepFilterNet, for very noisy recordings

Chain order: denoise -> EQ/dynamics -> silence trim -> mono/resample/encode.
EQ preset JSON (same format as the Podcast-Light-Edit-Chain voice-fitted presets):
  {"highpass_hz": 80, "eq": [{"f": 500, "width_octaves": 1.0, "gain_db": -3}],
   "compressor": {"threshold_db": -20, "ratio": 2.5, "attack_ms": 15, "release_ms": 200, "makeup_db": 2},
   "deess": 0.3}
Every key is optional.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Output presets. Speech ASR models are trained at 16 kHz mono; anything above is upload weight.
PRESETS = {
    # Safe everywhere (OpenRouter input_audio, AssemblyAI, Gemini, whisper.cpp).
    "asr": {"ext": "mp3", "codec": ["-c:a", "libmp3lame", "-b:a", "32k"], "rate": 16000},
    # Smallest upload for Gemini (direct API or OpenRouter accepts ogg). Opus holds speech well at 24 kbps.
    "gemini": {"ext": "ogg", "codec": ["-c:a", "libopus", "-b:a", "24k", "-application", "voip"], "rate": 16000},
    # Lossless 16 kHz for local models that want PCM (whisper.cpp, Parakeet/NeMo).
    "local": {"ext": "wav", "codec": ["-c:a", "pcm_s16le"], "rate": 16000},
    # Archive/evidence copy: small but comfortable to listen to.
    "archive": {"ext": "mp3", "codec": ["-c:a", "libmp3lame", "-b:a", "48k"], "rate": 22050},
}

# Silence trimming. The failure mode is cutting context, so the default only collapses long gaps.
VAD = {
    "off": None,
    # A pause of 6 s or more becomes 0.5 s. Thinking pauses mid-sentence survive.
    "conservative": {"min_silence": 6.0, "keep": 0.5, "threshold_db": -45},
    "moderate": {"min_silence": 3.0, "keep": 0.5, "threshold_db": -42},
    "aggressive": {"min_silence": 2.0, "keep": 0.3, "threshold_db": -40},
}


SHIPPED_EQ = Path(__file__).resolve().parent.parent / "templates" / "eq"


def eq_filters(spec: str) -> tuple[list[str], str]:
    path = SHIPPED_EQ / f"speech-{spec}.json" if spec in ("default", "phone", "headset") else Path(spec).expanduser()
    if not path.is_file():
        raise SystemExit(json.dumps({"error": f"EQ preset not found: {path}"}))
    pr = json.loads(path.read_text())
    f = []
    if pr.get("highpass_hz"):
        f.append(f"highpass=f={pr['highpass_hz']}")
    for b in pr.get("eq", []):
        f.append(f"equalizer=f={b['f']}:t=o:w={b.get('width_octaves', 1.0)}:g={b['gain_db']}")
    if c := pr.get("compressor"):
        f.append(f"acompressor=threshold={c['threshold_db']}dB:ratio={c['ratio']}:attack={c['attack_ms']}"
                 f":release={c['release_ms']}:makeup={c.get('makeup_db', 0)}dB")
    if pr.get("deess"):
        f.append(f"deesser=i={pr['deess']}")
    return f, str(path)


def denoise_step(mode: str, src: Path, workdir: Path, rnn_model: str | None) -> tuple[Path, list[str]]:
    """Returns (input for the main ffmpeg pass, extra filters to prepend)."""
    if mode == "afftdn":
        return src, ["afftdn=nr=12:nf=-50:tn=1"]
    if mode == "arnndn":
        if not rnn_model:
            raise SystemExit(json.dumps({"error": "--denoise arnndn needs --rnn-model <file.rnnn> "
                                                  "(models: github.com/GregorR/rnnoise-models)"}))
        return src, [f"arnndn=m={rnn_model}"]
    if mode == "deepfilter":
        exe = shutil.which("deep-filter") or shutil.which("deepFilter")
        if not exe:
            raise SystemExit(json.dumps({"error": "DeepFilterNet not found. Install the standalone binary "
                "(github.com/Rikorose/DeepFilterNet/releases, named deep-filter) or `uv tool install deepfilternet`; "
                "or use --denoise afftdn"}))
        wav = workdir / f"{src.stem}.48k.wav"  # DeepFilterNet works at 48 kHz
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vn", "-ac", "1",
                        "-ar", "48000", str(wav)], check=True)
        subprocess.run([exe, "-o", str(workdir / "df"), str(wav)], check=True, capture_output=True)
        out = next((workdir / "df").glob("*.wav"))
        return out, []
    return src, []


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size,bit_rate:stream=channels,sample_rate",
         "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = (d.get("streams") or [{}])[0]
    f = d.get("format", {})
    return {"duration_s": round(float(f.get("duration", 0)), 2), "bytes": int(f.get("size", 0)),
            "bitrate": int(f.get("bit_rate", 0) or 0), "channels": s.get("channels"),
            "sample_rate": int(s.get("sample_rate", 0) or 0)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--preset", choices=PRESETS, default="asr")
    ap.add_argument("--vad", choices=VAD, default="conservative")
    ap.add_argument("--min-silence", type=float, help="override: shortest silence (s) that gets collapsed")
    ap.add_argument("--keep", type=float, help="override: seconds of silence left in place of a collapsed gap")
    ap.add_argument("--threshold-db", type=float, help="override: level (dBFS) below which audio counts as silence")
    ap.add_argument("--eq", default="none",
                    help="none | default | phone | headset | path to a preset JSON (see above)")
    ap.add_argument("--denoise", choices=["none", "afftdn", "arnndn", "deepfilter"], default="none")
    ap.add_argument("--rnn-model", help="RNNoise model file for --denoise arnndn")
    ap.add_argument("-o", "--output", type=Path, help="default: <stem>.prep.<ext> next to the input")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(json.dumps({"error": f"{tool} not found on PATH"}))
            return 2
    if not a.input.is_file():
        print(json.dumps({"error": f"no such file: {a.input}"}))
        return 2

    p = PRESETS[a.preset]
    out = a.output or a.input.with_name(f"{a.input.stem}.prep.{p['ext']}")
    if out.resolve() == a.input.resolve():
        print(json.dumps({"error": "output would overwrite input"}))
        return 2

    import tempfile
    tmp = tempfile.TemporaryDirectory()
    src, filters = denoise_step(a.denoise, a.input, Path(tmp.name), a.rnn_model)
    eq_used = None
    if a.eq != "none":
        ef, eq_used = eq_filters(a.eq)
        filters += ef
    vad = dict(VAD[a.vad]) if VAD[a.vad] else None
    if vad or a.min_silence:
        vad = vad or dict(VAD["conservative"])
        if a.min_silence: vad["min_silence"] = a.min_silence
        if a.keep is not None: vad["keep"] = a.keep
        if a.threshold_db is not None: vad["threshold_db"] = a.threshold_db
        filters.append(
            "silenceremove=stop_periods=-1:stop_duration={min_silence}:stop_threshold={threshold_db}dB:"
            "stop_silence={keep}:detection=rms".format(**vad))

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vn"]
    if filters:
        cmd += ["-af", ",".join(filters)]
    cmd += ["-ac", "1", "-ar", str(p["rate"]), *p["codec"], str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(json.dumps({"error": "ffmpeg failed", "stderr": r.stderr[-2000:]}))
        return 1

    before, after = probe(a.input), probe(out)
    print(json.dumps({
        "input": str(a.input), "output": str(out), "preset": a.preset,
        "denoise": a.denoise, "eq": eq_used,
        "vad": vad and {"mode": a.vad, **vad},
        "before": before, "after": after,
        "trimmed_s": round(before["duration_s"] - after["duration_s"], 2),
        "size_ratio": round(after["bytes"] / before["bytes"], 3) if before["bytes"] else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
