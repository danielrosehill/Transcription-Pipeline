<!-- suffix: spec -->
The transcript below is someone talking through a piece of software or technical work they want done. Turn it into a development brief that an AI coding agent can act on cold.

Structure (omit a section if the transcript gives nothing for it):
# <short title>
## Goal: one or two sentences.
## Context: what exists now, repos, tools, constraints mentioned.
## Design: the structure the speaker described (stages, components, data flow), in the order it should be built, not the order it was spoken.
## Requirements: numbered, concrete, testable.
## Decisions and rationale: choices the speaker made and why, in their reasoning.
## Open questions: things the speaker left undecided, ambiguous or contradictory.
## Out of scope: anything the speaker ruled out.

Rules: keep every specific detail (names, versions, paths, numbers, preferences). Do not invent requirements. Where the speaker contradicted themselves, keep the later statement and list the contradiction under Open questions. Write in the imperative, plainly. Output only the brief in Markdown.
