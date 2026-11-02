# Google Drive

A folder link looks like `https://drive.google.com/drive/folders/<FOLDER_ID>`; a file link like
`https://drive.google.com/file/d/<FILE_ID>/view`. Use whichever Drive access the preferences name. Common ones:

**A Google Drive MCP / tool set** (search, list, download): list the folder's files, filter to audio MIME types
(`audio/*`, `video/*`), order by `modifiedTime` desc, download the newest to the working folder.

**rclone** (remote name from preferences, e.g. `gdrive:`):
```bash
rclone lsjson "gdrive:" --drive-root-folder-id <FOLDER_ID> --files-only | jq -r 'sort_by(.ModTime) | reverse | .[0:5][] | "\(.ModTime)\t\(.Name)"'
rclone copy "gdrive:<name>" ./ --drive-root-folder-id <FOLDER_ID>
```
Shared drives: add `--drive-shared-with-me` or `--drive-team-drive <ID>` as the user's remote needs.

**gws / gcloud-style CLIs:** `files.list` with `q="'<FOLDER_ID>' in parents and trashed=false"`, `orderBy=modifiedTime desc`, then `files.get?alt=media`.

After use: if the folder is an inbox the user empties (preferences say so), move the processed file to trash
or to a "done" subfolder, never delete permanently.
