# Chinese Subtitles Tool

This is a WIP (mostly the happy path) to add pinyin to a subtitle.
Current options are:

- chinese with pinyin
- other language with pinyin
- chinese with pinyin and other language

Current supported source subtitles are: `srt`, `ass` (embedded only ASS)

A single video file or a directory with multiple video files can be input.
Currently, if a directory is input it would use the first video in the directory to show the available subtitles information. Then the selected subtitle options would be used for the rest of the videos in the directory, which means all videos must have the same subtitle options.

To setup the project:

- `make start_venv`
- `make install`

To install development packages:

- `make install-dev`

To run the project:

- `make run`
