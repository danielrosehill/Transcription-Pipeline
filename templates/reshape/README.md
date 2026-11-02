# Reshape templates

Each file is a system prompt: the transcript (usually the cleaned one) goes in as the user turn.
Used by the `reshape-transcript` skill, run by the agent itself or sent out with `scripts/rewrite.py`.

Add your own in your preferences folder (`<prefs>/templates/<name>.md`); a user template with the
same name as a shipped one wins. A template can say what output file suffix it wants on its first
line as `<!-- suffix: spec -->`; otherwise the file name is the suffix.
