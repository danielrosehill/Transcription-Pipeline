# Unified Claude Code transcription plugin (collect, preprocess, transcribe, post-process, format, save)

## Goal
Build one public Claude Code plugin that runs the speaker's whole voice-note transcription workflow end to end, split into discrete stages, each a skill. It replaces their separate Gemini API, local-transcription and MCP-based plugins.

## Context
- The speaker has existing Claude Code plugins: one using the Gemini API for transcription, one for local on-device transcription, and MCP servers for these. The MCP layer is no longer considered necessary. Ship a plugin with environment variables and tell the agent to use the API directly.
- The old Gemini MCP repo should be marked end of life / no longer maintained (update its README). This plugin is its successor.
- Current capture workflow: record on a phone in the ASR app, upload to a predefined Google Drive folder (e.g. "development plans", "audio context"). Audio may also be recorded on a computer in Audacity and saved to a local folder called "Voice Notes".
- The speaker runs an AI/MCP gateway on a home server. Agents connect to the server, which holds the CLIs, connections, tools, MCPs, plugins and skills. Tools needing binaries run on a different filesystem from the user's machine.
- Workaround already in use: a MinIO (S3) instance on the home server with a bucket named "File Staging" that has an expiry policy. This is specific to the speaker's environment and must not be hardcoded in the public plugin.
- Plugins are shipped public and adapted by the user. The speaker used to keep parallel private plugins and now wants a single public plugin they can adapt. A private plugin with their own practices on top of a blank-slate public one is the fallback.
- Plugins must be framework agnostic (usable in Codex, not only Claude Code), so they must not rely on Claude's internal memory.
- Assume tools such as Google Drive access are already set up in the environment. Do not build MCP wrappers for them.

## Design
Build in this order, one skill (with sub-skills) per stage.

### 0. Persistent user config ("scratch pad") and onboarding
- Store user preferences in a plain file on the user's local filesystem. Do not use agent-internal memory.
- Provide an onboarding skill where the user pastes Google Drive folder links/IDs with labels (e.g. "development plan voice notes", "general voice notes"). Save them to the scratch pad.
- The scratch pad also holds OpenRouter model entries (see stage 3), the staging bucket details, EQ and preprocessing presets, speaker names, and similar settings.

### 1. Collection / retrieval
- A `retrieve` skill with sub-skills:
  - Google Drive
  - Wasabi
  - S3
  - Local files (e.g. the "Voice Notes" folder)
- Each sub-skill assumes its tool or connection is already available in the environment.

### 2. Upload / staging (remote-filesystem case)
- If the audio is on the user's machine and the transcription tool runs on a different machine (the gateway server), transfer the file to a configurable S3-compatible staging bucket, then invoke the transcription skill against it.
- Prefer this transfer over base64-uploading the file directly. Base64 worked poorly for long recordings.

### 3. Preprocessing (runs before inference, for local and remote)
- **Downsampling/format:** convert stereo to mono and reduce the bitrate/sample rate to what the target model expects. Provide a sane default and a Gemini API-specific variant.
- **VAD and silence truncation:** trim silence to cut upload size. The default preset must be conservative. Example: a silence of about 6 seconds is trimmed to about 0.5 seconds.
- **EQ preset:** ship a generic EQ preset. Let users keep customised presets outside the main plugin.
- **Optional deep-learning denoise:** an opt-in step for very noisy recordings, applied before upload.

### 4. Transcription
A single transcription skill routes to sub-skills:
- **AssemblyAI:** the default for long-form transcription. It gives timestamps and is affordable.
- **OpenRouter:** for day-to-day use.
  - Default model: Gemini Flash Latest (a dynamic endpoint, so new Flash releases need no update).
  - Default system prompt along the lines of: "You are receiving audio, return a full transcript without disfluencies."
  - Keep a list of four or five OpenRouter models in the user scratch pad, not the public plugin. Use the keys OR1, OR2, OR3... for the endpoint and OR1 notes, OR2 notes... for freehand usage notes (e.g. "use when the user asks for Mistral Large or the most cost-effective transcription").
- **Local inference:** route to a model such as Parakeet or Whisper running on the user's machine or home server.

### 5. Post-processing
- Always save the original verbatim output as `raw.txt`. If timestamps are returned, also save `raw.srt`.
- **Cleanup**, in levels:
  - **Light (default):** add paragraph spacing, remove disfluencies and false starts.
  - **Medium:** also add headings and remove clear redundancy where the speaker repeated themselves.
  - **Heavy:** also correct likely ASR mistranscriptions to the inferred intended word. This is the riskiest level.
- By default the agent does the cleanup itself. Optionally, send the raw text via API to a cloud LLM or to Superwhisper's "S1 Mini" model.
- **Restructuring** into a target format, with the agent by default or an external tool optionally. The user supplies the target format and style directions. Examples: development brief (`spec.md`), to-do list, blog outline, blog post, meeting minutes/summary.
- **Diarization:** when a provider returns generic labels (Speaker 1, 2, 3), map them to named speakers. The user either states who is who (e.g. the male voice is the speaker, the female voice is Hannah) or identifies a sentence or two from a clip, and the agent infers the rest.
- Keep every artifact (raw, cleaned, restructured). Never keep only the cleaned version.

### 6. Formatting (final step)
- Render output into final documents. Example: use Typst to build a PDF of a diarized call transcript with speech bubbles and a title (e.g. "Family meeting discussing vacation plans").
- Skills should be mixable, e.g. a summary of key decisions as minutes rather than a full verbatim transcript.

### 7. Saving
- Save outputs to a configurable target. Most commonly this is inside the current GitHub repo.
- Another target is a user-defined "transcribed" folder in Google Drive, with subfolders per voice-note type.
- Optionally notify the user when done, e.g. email a link.

## Requirements
1. Package everything as one public plugin with one skill per stage and sub-skills for providers and sources. Do not include MCP servers.
2. Configure providers through environment variables. Skills instruct the agent to use the provider APIs directly.
3. Persist all user customisation in a local, framework-agnostic file. Do not use Claude's internal memory.
4. Provide an onboarding skill that collects labelled Google Drive folder links/IDs from pasted text and writes them to the scratch pad.
5. Provide `retrieve` sub-skills for Google Drive, Wasabi, S3 and local filesystem.
6. When the audio is local and the tooling is remote, upload it to a user-configured S3-compatible staging bucket before transcription. Do not hardcode the speaker's MinIO/"File Staging" setup.
7. Provide a preprocessing skill with downsampling (stereo to mono, bitrate reduction, default and Gemini-specific presets) and VAD/silence trimming. The default VAD preset must be conservative.
8. Preprocessing must support an EQ preset. Ship a generic one and allow user-customised presets stored outside the main plugin.
9. Preprocessing must offer an optional deep-learning denoise step for very noisy recordings, applied before upload.
10. Provide transcription sub-skills for AssemblyAI, OpenRouter (default Gemini Flash Latest with the cleanup system prompt above) and local inference (e.g. Parakeet/Whisper).
11. Read OpenRouter model entries (endpoint plus freehand notes) from the user scratch pad, using the OR1/OR1 notes naming.
12. Always write the verbatim output as `raw.txt`, plus `raw.srt` when timestamps are available.
13. Implement light, medium and heavy cleanup levels, with light as the default. Do cleanup via the agent by default, with an optional API call to a cloud LLM or Superwhisper S1 Mini.
14. Provide open-ended restructuring that takes a user-specified format and style, including a development brief producing `spec.md`.
15. Provide diarization with user-supplied speaker names, via inference or via the user labelling a short clip.
16. Provide PDF output via Typst, including a speech-bubble transcript layout.
17. Save outputs to the current repo, or to a configured Google Drive folder/subfolder.
18. Keep all intermediate artifacts (raw, cleaned, final).
19. When creating a repo from a voice note, ask whether to include the processed recording in the repo as a record of the thinking. Do not assume it should be private, even for a public repo.
20. When the recording is included, the repo README must link to it under a heading titled "Original idea recording".
21. Update the old Gemini MCP repo's README to mark it end of life / no longer maintained, pointing to this plugin.

## Decisions and rationale
- **Drop MCPs:** a plugin plus env vars and agent instructions is simpler, and plugins have matured enough that MCPs are unnecessary for defining these tasks.
- **Public plugin plus user adaptation, no private forks:** this is easier to maintain, even for the speaker's own use.
- **Scratch-pad file instead of rewriting skills:** an agent that rewrites shipped skills for the user's environment creates a local fork, and plugin updates then conflict. Notes in a scratch file avoid that.
- **File-based memory instead of agent-internal memory:** keeps the plugin usable in other harnesses (e.g. Codex).
- **Staging bucket instead of base64 upload:** base64 fails for long recordings, and remote tools cannot see the user's local files.
- **Gemini Flash Latest as the OpenRouter default:** it is dynamic, so it needs no updates, it is cheap, and it is good enough for basic transcription.
- **AssemblyAI for long-form:** timestamped, purpose-built, affordable.
- **Conservative VAD default:** the failure mode of over-aggressive VAD is lost context.
- **Preprocess for both local and remote inference:** smaller files and the right format help either way.
- **Always keep raw output and all artifacts:** text is lightweight and the original verbatim version may matter later.
- **Agent does post-processing by default:** the API route is an option, not the default.
- **Compliance-style output set:** for the family/school-plans example, save the final PDF plus `raw.txt` plus the downsampled audio to Google Drive. This is proof if someone disputes what was said or something was mistranscribed.

## Open questions
- **Contradiction on kept artifacts:** the speaker first said to keep raw plus cleaned plus restructured and never just the cleaned version. In the end-to-end example they said the ideal output was the PDF, `raw.txt` and the downsampled audio in Google Drive. They flagged this as a deliberate contradiction. The later statement is the one to follow for that example, so decide whether the cleaned text is also saved there.
- How to resolve plugin updates versus user customisation in general. The speaker has no answer yet, so use the scratch pad for now.
- The scratch-pad file location and format are unspecified.
- The exact audio format and bitrate the Gemini API expects is unknown (the speaker could not remember it). It needs research for the Gemini preset.
- Exact VAD thresholds are unspecified. The only example is about 6 seconds of silence trimmed to about 0.5 seconds (the speaker also said "instead of 10"). The plugin name is unspecified.
- Where preprocessing runs when the file is local but the tooling is on a remote server is unspecified. The denoise step is "before upload", so decide whether all preprocessing runs locally before staging.
- The EQ preset format, the denoise model and the location for user presets outside the plugin are unspecified.
- The mechanism for emailing a Drive link when finished is unspecified.
- The Wasabi/S3 retrieval details and credential handling are unspecified.
- The Typst templates and PDF layout details are unspecified beyond speech bubbles and a title.

## Out of scope
- MCP servers for this plugin. The old Gemini MCP is only marked end of life.
- Rewriting or forking shipped skills to match a user's environment.
- Relying on agent-internal memory for persistence.
- Hardcoding the speaker's personal environment (MinIO "File Staging" bucket, specific Drive folders, speaker names, the OR model list) into the public plugin. That belongs in the user's scratch pad or a private plugin.
