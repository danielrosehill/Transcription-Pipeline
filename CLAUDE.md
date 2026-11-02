# Transcription-Pipeline (agent notes)

Public agent-skills plugin `transcription-pipeline`, repo `danielrosehill/Transcription-Pipeline`, created 2026-11-02.
Listed in the `danielrosehill` marketplace (`danielrosehill/Claude-Code-Plugins`, `.claude-plugin/marketplace.json`).
Release tier: **medium** (tags `v3.00`, `v3.01`...; `plugin.json` keeps semver for the plugin loader).

## Layout
- `skills/<stage>/SKILL.md`: one skill per pipeline stage; backend-specific detail in `references/`.
- `scripts/`: `preprocess.py`, `transcribe.py`, `rewrite.py`. uv inline-dependency scripts, JSON to stdout, never
  overwrite inputs. Test them on a real clip after any change (all four backends were run on 2026-11-02).
- `templates/`: prompts (transcription, cleanup, speaker labels), reshape templates, EQ presets, Typst templates,
  `preferences.example.md`.
- `idea/`: the voice note this plugin was specified from, with raw/clean/spec transcripts. Not loaded by the plugin.
- `docs/prior-art.md`: what this replaced and what was carried over or dropped.

## Rules
- Public plugin: nothing about one user's infrastructure (hosts, IPs, bucket names, secrets tooling) goes in this
  repo. That belongs in the user's preferences file.
- Skills must work in any agent: plain paths, env vars, no reliance on one vendor's memory.
- No MCP servers. If a backend needs a client, it goes in `scripts/transcribe.py`.
