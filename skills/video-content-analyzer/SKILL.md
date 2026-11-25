---
name: video-content-analyzer
description: Analyze video content (speech-to-text, dialogue summary, and visual screen content like GitHub repos, websites, or code shown on screen) from online URLs (without downloading full video) or local video/audio files.
---

# Video Content Analyzer Skill

Use this skill whenever the user asks to analyze what is being **said or shown** in a video or audio file (e.g., "এই ভিডিওতে কী বলেছে?", "ভিডিওতে কোন গিটহাব রেপো বা টুল দেখালো?", "ভিডিওর সামারি দাও", "অডিওতে কী আলোচনা হয়েছে?").

Supports both **online streaming URLs** (YouTube, Facebook, X, direct links) without downloading the full video, and **local files** in phone storage.

---

## Capabilities & Architecture
1. **Zero-Download Online Analysis**: Extracts direct audio/video streams via `yt-dlp` and `ffmpeg` without saving multi-gigabyte video files to disk.
2. **Smart 3-Tier Speech Understanding**:
   - **Tier 1 (Online Subtitles)**: Tries direct/auto-generated subtitles first for instant speed (0 MB audio, 0% CPU).
   - **Tier 2 (crouter Google API)**: Checks `~/.gemini/claude-router/config.json` for a `googlestudio` API key and verifies that `gemini-3.5-transcribe` is active. Sends lightweight compressed MP3 chunks for fast, accurate multilingual transcription with timestamps and **0% phone heat**.
   - **Tier 3 (Whisper Fallback with Mandatory Duration Confirmation)**: If `crouter` has no Google API key or the Google model fails/is inactive, `video-analyzer` reports the exact reason, checks the audio duration, and exits with **code 2** (`WHISPER_CONFIRMATION_REQUIRED`) so the user can choose how much audio to transcribe in a single `1.25x` pass (`-t 3`).
3. **Visual Frame Capture**:
   - Automatically detects moments when speakers mention repos, tools, websites, links, or code (e.g., *"এই রেপোটি..."*, *"on my screen..."*, *"link in description"*).
   - Snaps exact video frames at those specific timestamps using FFmpeg.
4. **Visual Intelligence**:
   - Read the captured snapshot frames to extract repo names (`owner/repo`), URLs, or terminal commands shown on screen.

---

## How to Execute

### 1. Run the Video Analyzer
Run the single command in terminal:
```bash
video-analyzer "<VIDEO_URL_OR_LOCAL_PATH>" -o "$HOME/.antigem/media_analysis"
```

### 2. Handle Whisper Fallback Confirmation (Exit Code 2)
If `video-analyzer` exits with **code 2** and prints `WHISPER_CONFIRMATION_REQUIRED: {...}`:
1. **NEVER** run `whisper-cli` directly on the full audio without asking.
2. Parse the JSON payload (`google_message`, `source_duration_formatted`, `suggested_options`).
3. **Immediately use `ask_question`** to inform the user:
   - Why Google API wasn't used (e.g., not set in `crouter`, or the exact model/API error), and
   - The total audio duration (e.g., `12m 30s`),
   - Offer multiple-choice options for how much to transcribe (`First 30 seconds (Recommended)`, `First 2 minutes`, `First 5 minutes`, `Full audio`).
4. Re-run `video-analyzer` with `--allow-whisper` and `--max-duration <seconds>` (omit `--max-duration` only if the user selected `Full audio`).

### 2. Inspect the Generated Manifest & Transcripts
The tool generates:
- `$HOME/.antigem/media_analysis/analysis_manifest.json`: JSON summary of dialogues, timestamps, and captured frames.
- `$HOME/.antigem/media_analysis/frames/`: Individual frame snapshots (`frame_1_45s.jpg`, etc.) taken at crucial moments when tools or repos were mentioned.
- `$HOME/.antigem/media_analysis/*_sub.srt`: Complete timestamped dialogue transcript.

### 3. Read the Frames & Answer the User
- Review the `analysis_manifest.json` for what was spoken at each moment.
- Inspect the captured frame images using file viewing/reading tools to read the screen text (GitHub repository URLs, project names, UI buttons, code snippets).
- Provide a clear, comprehensive breakdown to the user detailing:
  1. **Topic / Summary**: What the video is about.
  2. **Spoken Content**: Key points discussed.
  3. **Visual Findings**: Names of GitHub repos, tools, links, or commands shown on screen with exact timestamps.
  4. **Cache Cleanup Link**: Always provide clickable `file://` links to:
     - The main **delete** folder: `file:///data/user/0/ai.antigem/files/home/.antigem/media_analysis/delete` (opens the root delete folder to see all cached projects).
     - The specific project cache folder (`delete_cache_dir` from `analysis_manifest.json`).
     - Mention that temporary audio chunks, wav files, and frame snapshots (SS) have all been safely moved into this folder so they can be deleted whenever needed.
