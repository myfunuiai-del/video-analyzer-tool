<div align="center">

<img src="./assets/logo.svg" alt="Video Analyzer Tool Logo" width="100%" />

<p align="center">
  <b>Zero-Download AI Video Intelligence, Speech Transcription & Visual Frame Extraction</b>
</p>

[![Platform](https://img.shields.io/badge/Platform-Android%20Termux%20%7C%20Linux-brightgreen.svg?style=for-the-badge&logo=android)](https://github.com/myfunuiai-del/video-analyzer-tool)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python)](https://github.com/myfunuiai-del/video-analyzer-tool)
[![Whisper.cpp](https://img.shields.io/badge/Powered%20By-Whisper.cpp-purple.svg?style=for-the-badge&logo=openai)](https://github.com/ggerganov/whisper.cpp)
[![License](https://img.shields.io/badge/License-MIT-orange.svg?style=for-the-badge)](https://github.com/myfunuiai-del/video-analyzer-tool)

</div>

---

<div align="right">

**🌐 Language / ভাষা:** &nbsp; **English** &nbsp;|&nbsp; **[🇧🇩 বাংলা সংস্করণ (README_BN.md)](./README_BN.md)**

</div>

---

## 📖 Overview

**Video Analyzer Tool** is a high-speed, resource-optimized AI video intelligence and speech analysis CLI tool. It operates without downloading multi-gigabyte video files by directly tapping into remote media streams (Facebook Reels/Videos, YouTube Shorts/Videos, X, and direct media URLs) or local media files. It generates speech-to-text transcripts, trims silence, aligns timestamps with the original source, and captures targeted visual key-moment frames.

---

## 🌟 Key Features

* 🚀 **Zero Full Video Download**: Analyze online video streams directly via `yt-dlp` and `ffmpeg` without storing heavy video files locally.
* ✂️ **Smart Silence Trimming with Boundary Padding**: Cuts dead silence while retaining natural 80ms boundaries to prevent clipped syllables.
* ⏱️ **Automatic Timeline Remapping**: Subtitles and extracted snapshot frames are mapped back cleanly to the source video's original timeline.
* 🛡️ **Anti-Overheating Speed Probing**: Probes long videos (>120s) with a fast 60s sample test at 1.25x speed, preventing repeated full-length transcription runs and keeping mobile devices cool.
* 🎯 **Targeted Visual Frame Capture**: Scans transcripts for keywords (`github`, `repo`, `tool`, `code`, `link`, `screen`) and captures HD frames with token-refresh safeguards.
* 🌐 **Multilingual & Mixed-Language Support**: Seamlessly recognizes Bengali, English, and mixed conversational Banglish.

---

## 🧠 Whisper Models Guide (Speed & Bengali Accuracy)

Powered by quantized models in `whisper.cpp`:

| Model Name | File Name | Size | Recommended Use Case | Speed Rating |
| :--- | :--- | :--- | :--- | :--- |
| **Bengali Medium (Fine-Tuned)** ⭐ | `ggml-bn-medium-q5_0.bin` | ~539 MB | **Best for Pure Bengali audio.** Exceptionally accurate pronunciation and grammar handling. | ⚡⚡⚡ (Balanced) |
| **Large v3 Turbo (Fast & Accurate)** ⚡ | `ggml-large-v3-turbo-q5_0.bin` | ~574 MB | **Fastest & Most Accurate.** Top choice for English, mixed Banglish, and general speech. | ⚡⚡⚡⚡⚡ (Ultra Fast) |
| **Base Model (Lightweight)** 🪶 | `ggml-base.bin` | ~148 MB | **Fast language identification** and lightweight transcription on low-RAM devices. | ⚡⚡⚡⚡ (Very Fast) |
| **Small Model (General)** | `ggml-small.bin` | ~487 MB | Balanced trade-off between speed and accuracy. | ⚡⚡⚡ (Good) |

> 💡 **Default Models Directory:** `$HOME/tools/whisper.cpp/models/`

### Download Models:
```bash
mkdir -p "$HOME/tools/whisper.cpp/models" && cd "$HOME/tools/whisper.cpp/models"

# Large v3 Turbo (Fastest & General Multi-language)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin

# Base Model (Language Detection)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/myfunuiai-del/video-analyzer-tool.git
cd video-analyzer-tool

# Run setup script
chmod +x install.sh
./install.sh
```

---

## 💻 Usage & CLI Examples

```bash
# Facebook Reels or Videos:
video-analyzer "https://www.facebook.com/share/v/1DUg7LdCX4/"

# YouTube Shorts or Full Videos:
video-analyzer "https://youtube.com/shorts/vmD2IHFSutY"

# Local Video on Device Storage:
video-analyzer "/sdcard/Download/my_video.mp4"

# Custom Output Directory:
video-analyzer "https://youtube.com/watch?v=..." -o "./custom_output"
```

---

## 📂 Output Structure

Each run outputs to a unique run folder under `~/.antigem/media_analysis/`:

```text
~/.antigem/media_analysis/<run_hash>_<timestamp>/
├── analysis_manifest.json            # Complete JSON metadata, drift score & timing maps
├── transcript_clean.txt              # Clean readable transcript without rolling loops
├── whisper_sub_original_timeline.srt   # SRT subtitles synchronized with original timeline
├── audio_1p25x_16k_mono.wav          # Processed 16kHz audio file
└── frames/                           # Extracted visual key frames
    ├── frame_1_15s_direct.jpg
    └── frame_2_82s_segment.jpg
```

---

## 🤝 Contribution & License

Open for personal and open-source contributions. Distributed under the MIT License.
