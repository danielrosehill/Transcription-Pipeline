# Transcription preferences

<!--
This file is the plugin's memory of how YOU work. Every skill reads it before acting and
nothing in it is required: a missing section means "use the plugin default".
Location: $TRANSCRIPTION_PREFS_DIR, else $CLAUDE_USER_DATA/transcription-pipeline/,
else ~/.claude-user-data/transcription-pipeline/. Plain Markdown so any agent (Claude Code,
Codex, Gemini CLI...) and you can read and edit it. The `setup` skill writes it.
Keep secrets OUT of this file: name the environment variable that holds a key, never the key.
-->

## Sources (where recordings arrive)

| Name | Kind | Location | Used for |
|---|---|---|---|
| dev-plans | google-drive | https://drive.google.com/drive/folders/<id> | voice notes describing software to build |
| general | google-drive | https://drive.google.com/drive/folders/<id> | everything else |
| desktop | local | ~/Recordings/Voice Notes | Audacity recordings on this machine |

How this environment reaches Google Drive: <e.g. "rclone remote gdrive:", "the google-drive MCP tools", "gws CLI">
How this environment reaches S3-compatible storage: <e.g. "aws CLI profile minio", "rclone remote s3:">

## Staging (only if your agent's tools run on another machine than your files)

<e.g. "Upload with `rclone copyto <file> s3:transient/<name>` then presign with `rclone link --expire 1h`; the bucket expires objects after 1 day.">

## Keys

| Backend | Env var |
|---|---|
| openrouter | OPENROUTER_API_KEY |
| assemblyai | ASSEMBLYAI_API_KEY |
| gemini | GEMINI_API_KEY |

How keys reach the environment: <e.g. "already exported", "prefix commands with `doppler run --`">

## Transcription defaults

- Default backend: openrouter
- Long-form (> 20 min) or timestamps or several speakers: assemblyai
- Default transcription prompt mode: raw

### OpenRouter model slots

| Slot | Model | When to use |
|---|---|---|
| or1 | ~google/gemini-flash-latest | default; cheap, follows new Flash releases |
| or2 | google/gemini-3.5-flash-lite | cheapest |
| or3 | mistralai/voxtral-small-24b-2507 | second opinion |

### Local / self-hosted ASR

| Name | Base URL (OpenAI-compatible) | Model | Notes |
|---|---|---|---|
| home-server | http://<host>:<port> | <model id> | <when to use> |

## Preprocessing

- EQ preset: none   <!-- none | default | phone | headset | path to your own JSON in this folder -->
- Denoise: none     <!-- none | afftdn | deepfilter -->
- Silence trimming: conservative

## Post-processing

- Cleanup level: light   <!-- light | heavy -->
- Executor: agent        <!-- agent | openrouter:<model> | <base-url>:<model> -->
- Always keep: raw transcript + cleaned
- Known speakers: <e.g. "Daniel (male), Hannah (female)">
- Vocabulary the ASR gets wrong: <names, products, jargon, one per line>

## Output sets (named recipes)

- dev-brief: raw + cleaned + spec (reshape dev-spec), saved in the current repo under `idea/`
- call: assemblyai with speakers, label-speakers, cleaned (light), minutes, PDF (conversation)
<add your own>

## Save targets

| Name | Kind | Location | For |
|---|---|---|---|
| repo | repo | ./idea/ (or ./transcripts/) | anything recorded about the current repo |
| drive-transcripts | google-drive | https://drive.google.com/drive/folders/<id> | finished transcripts, subfolders per output set |

- Include the recording itself when saving to a repo: ask   <!-- ask | yes | no -->
