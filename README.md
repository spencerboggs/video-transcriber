# Video Transcriber
A Python script to automate video transcription, subtitle generation, and subtitle embedding for video files (.mp4, .mov). This tool is designed for efficient speech recognition and video enhancement with text overlays.

## Features
* Transcribes audio from video files and saves the transcription as a .txt file.
* Converts audio to .wav format for analysis using Whisper.
* Generates .srt subtitle files with accurate timing.
* Overlays subtitles directly onto videos and exports as .mp4.
* Supports batching for multiple video files in the videos folder.

## Dependencies
The project requires the following Python libraries:
* whisper
* numpy
* moviepy
* Pillow

Installing the libraries:
```
pip install -r requirements.txt
```

## Directory Structure
* `videos/` – Input folder for video files (.mp4 or .mov).
* `transcripts/` – Stores generated transcription files (.txt) and subtitles (.srt).
* `wav_files/` – Contains .wav files extracted from videos.
* `subtitles/` – Stores videos with embedded subtitles.

## Usage
1. Place video files into the `videos/` folder
2. Run the script:
```
python main.py
```
3. Answer the terminal prompts to generate the video with subtitles
