The transcript below has generic speaker labels (Speaker A/B, Speaker 1/2...). Replace them with the speakers' real names using the mapping and hints the user gives after the transcript.

- Apply the mapping consistently to every turn. If the user gave only descriptions ("the male voice is Daniel"), infer the mapping from content: who is addressed by name, who refers to their own work, role and context. Say which evidence settled each label in one line at the very top, inside an HTML comment.
- If a turn is clearly mis-attributed (one speaker answering their own question), fix the label; never change the words.
- Merge consecutive turns by the same speaker.
- Output format, one paragraph per turn: **Name:** text
- Output only the relabelled transcript (plus the one-line HTML comment).
