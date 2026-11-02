# Local files

- A path: use it. Check it exists and is audio/video (`ffprobe -v error -show_entries format=duration,format_name -of json <file>`).
- A named folder from preferences: newest audio file there.

```bash
find "<folder>" -maxdepth 1 -type f \( -iname '*.mp3' -o -iname '*.m4a' -o -iname '*.wav' -o -iname '*.ogg' -o -iname '*.opus' -o -iname '*.flac' -o -iname '*.aac' -o -iname '*.webm' -o -iname '*.mp4' \) -printf '%T@\t%p\n' | sort -rn | head -5
```

Copy the file into the working folder only if outputs will be saved there and the user wants the recording kept with them; otherwise read it in place.
Video files work: `preprocess-audio` drops the video stream.
