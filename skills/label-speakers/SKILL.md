---
name: label-speakers
description: Replace generic speaker labels (Speaker A/B, Speaker 1/2) in a diarized transcript with real names, from a mapping the user gives, from voice descriptions ("I'm the male voice, Hannah is the female voice"), or from short clips the user listens to and identifies. Use after a multi-speaker transcription, or on "who's who", "label the speakers", "diarize this as me and X".
---

# Label speakers

Input: a transcript with generic labels (`<stem>.raw.txt` from AssemblyAI with speakers, or `<stem>.clean.md`).
Output: `<stem>.labelled.md`; the input stays as it is.

Get the names from, in order: the request, the **Known speakers** line in preferences, or the user.

## Ways to settle who is who

1. **From content** (default, free): use `templates/prompts/label-speakers.md`. Names said aloud, who asks and who
   answers, who talks about their own job or plans. Fine for two or three distinct people.
2. **From descriptions** ("I'm the male voice"): AssemblyAI does not say which label is which voice, so combine the
   description with content clues as in 1. If still unsure, use 3.
3. **By ear:** cut a short sample per label and let the user identify them. Take each label's first turn of at
   least 5 seconds from `<stem>.raw.json` (`utterances[].speaker/start/end`, in ms):
   ```bash
   ffmpeg -loglevel error -ss <start_s> -t 6 -i <audio> speaker-A.mp3
   ```
   Give the user the files (or the timestamps) and ask "which is A, which is B". Write the answer into the mapping.

Apply the mapping to every turn, merge consecutive turns by the same person, never change words. Report the
mapping and how it was decided in one line. If the user says a speaker is unchanged across recordings (the same
household, a regular call), offer to save the description in preferences.
