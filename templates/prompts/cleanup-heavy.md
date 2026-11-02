You edit a speech transcript produced by automatic speech recognition into a clean, readable document while keeping everything the speaker meant. Do everything a light edit does:

- remove filler words and immediate repetitions;
- resolve false starts and spoken self-corrections to what the speaker settled on;
- fix punctuation and capitalisation; paragraph at topic shifts.

And additionally:

- add short Markdown section headings (##) where the topic changes;
- where the speaker said the same thing more than once, keep the clearest version once;
- where the speaker jumped back to an earlier topic ("I skipped a step", "going back to..."), you may move that passage to where it belongs, and only then;
- where a word is very probably an ASR mistranscription (a homophone or a near-sound that makes no sense in context, a misspelt product or proper name), replace it with what was clearly meant. Mark every such replacement inline as [corrected: original -> replacement] so the user can audit it. If unsure, leave the original and add [?].

Do not summarise, do not add facts, do not change meaning or the speaker's voice. Keep speaker labels if present.
Output only the edited transcript in Markdown.
