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

**🌐 Language / ভাষা:** &nbsp; **[🇧🇩 বাংলা](#-বাংলা-সংস্করণ)** &nbsp;|&nbsp; **[🇬🇧 English](#-english-version)**

</div>

---

# 🇧🇩 বাংলা সংস্করণ

## 📖 পরিচিতি (Overview)

**Video Analyzer Tool** হলো একটি দ্রুতগতির ও রিসোর্স-অপ্টিমাইজড এআই ভিডিও বিশ্লেষণ টুল। এটি পুরো ভিডিও ডাউনলোড না করেই রিমোট স্ট্রিমিং লিঙ্ক (Facebook Reel/Watch, YouTube Shorts/Video, X/Direct Video) কিংবা লোকাল ভিডিও ফাইল থেকে অত্যন্ত দ্রুত গতিতে স্পিচ টু টেক্সট (অডিও ট্রান্সক্রিপশন), সাইলেন্স ট্রিম, টাইমস্ট্যাম্প রিম্যাপিং এবং গুরুত্বপূর্ণ ভিজ্যুয়াল ফ্রেম স্বয়ংক্রিয়ভাবে ক্যাপচার করে।

---

## 🌟 মূল সুবিধাসমূহ (Key Features)

* 🚀 **Zero-Download Streaming**: মাল্টি-গিগাবাইট ভিডিও ডাউনলোড করার দরকার নেই; `yt-dlp` ও `ffmpeg` দিয়ে রিমোট স্ট্রিম থেকে সরাসরি অডিও/ভিডিও অ্যানালাইসিস করে।
* ✂️ **Smart Silence Trimming with Boundary Padding**: কথার মাঝের অতিরিক্ত নীরবতা স্বয়ংক্রিয়ভাবে বাদ দিয়ে প্রসেসিং টাইম কমায় এবং ৮০ms প্যাডিং নিশ্চিত করে কোনো শব্দ যাতে না কাটে।
* ⏱️ **Automatic Timeline Remapping**: ট্রিম হওয়া অডিওর সাবটাইটেল এবং স্ক্রিনশট ফ্রেমের সময় স্বয়ংক্রিয়ভাবে মূল ভিডিওর আসল টাইমলাইনের সাথে নিখুঁতভাবে সমন্বয় (remap) হয়ে যায়।
* 🛡️ **Anti-Overheating Speed Probing**: ১৫–৩০ মিনিটের লম্বা ভিডিওর জন্য বারবার পুরো ফাইল ট্রান্সক্রাইব না করে ৬০ সেকেন্ডের ছোট স্যাম্পল টেস্ট করে দ্রুততম ও সেরা অ্যাকুরেট স্পিড বেছে নেয়।
* 🎯 **Targeted Visual Frame Capture**: ট্রান্সক্রিপ্টে উল্লেখিত গুরুত্বপূর্ণ কি-ওয়ার্ড (যেমন: GitHub repo, link, tool, code, website) শনাক্ত করে সেই মুহূর্তের এইচডি ফ্রেম সংরক্ষণ করে।

---

## 🧠 Whisper মডেল গাইড (Bengali & Fast Models)

ভিডিও অ্যানালাইজার স্ক্রিপ্টটি `whisper.cpp` এর কোয়ান্টাইজড মডেলের সাহায্যে কাজ করে:

| মডেলের নাম | ফাইলের নাম | সাইজ | কার্যকারিতা ও কোন ক্ষেত্রে সেরা | স্পিড রেটিং |
| :--- | :--- | :--- | :--- | :--- |
| **Bengali Medium (Fine-Tuned)** ⭐ | `ggml-bn-medium-q5_0.bin` | ~539 MB | **খাঁটি বাংলা (Pure Bengali) ভাষার জন্য সেরা।** উচ্চারণ ও ব্যাকরণ অত্যন্ত নিখুঁতভাবে ধরতে পারে। | ⚡⚡⚡ (সুষম) |
| **Large v3 Turbo (Fast & Accurate)** ⚡ | `ggml-large-v3-turbo-q5_0.bin` | ~574 MB | **সবচেয়ে দ্রুত ও অ্যাকুরেট।** ইংরেজি, মিশ্র ভাষা (Banglish) এবং সাধারণ স্পিচের জন্য প্রথম পছন্দ। | ⚡⚡⚡⚡⚡ (চরম দ্রুত) |
| **Base Model (Lightweight)** 🪶 | `ggml-base.bin` | ~148 MB | **দ্রুত ভাষা শনাক্তকরণ (Language Detection)** ও অল্প র‍্যামের ফোনে সুপারফাস্ট ট্রান্সক্রিপশন। | ⚡⚡⚡⚡ (খুব দ্রুত) |
| **Small Model (General)** | `ggml-small.bin` | ~487 MB | মিডিয়াম ও বেসের মাঝামাঝি সাধারণ ব্যালান্সড পারফরম্যান্স। | ⚡⚡⚡ (ভালো) |

> 💡 **মডেল ডিরেক্টরি পাথ:** `$HOME/tools/whisper.cpp/models/`

### মডেল ডাউনলোড কমান্ড:
```bash
mkdir -p "$HOME/tools/whisper.cpp/models" && cd "$HOME/tools/whisper.cpp/models"

# লার্জ ভি৩ টার্বো মডেল
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin

# বেস মডেল (ল্যাঙ্গুয়েজ ডিটেকশন)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

---

## 🛠️ ইনস্টলেশন (Installation)

```bash
# রিপোজিটরি ক্লোন করুন
git clone https://github.com/myfunuiai-del/video-analyzer-tool.git
cd video-analyzer-tool

# সেটআপ স্ক্রিপ্ট চালান
chmod +x install.sh
./install.sh
```

---

## 💻 ব্যবহার বিধি (Usage Examples)

```bash
# ফেসবুক ভিডিও বা রিল:
video-analyzer "https://www.facebook.com/share/v/1DUg7LdCX4/"

# ইউটিউব শর্টস বা ভিডিও:
video-analyzer "https://youtube.com/shorts/vmD2IHFSutY"

# লোকাল ভিডিও ফাইল:
video-analyzer "/sdcard/Download/my_video.mp4"
```

<div align="right">
  <a href="#-language--ভাষা--বাংলা-সংস্করণ--english-version">⬆️ শীর্ষে যান / Back to Top</a>
</div>

---

# 🇬🇧 English Version

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

<div align="right">
  <a href="#-language--ভাষা--বাংলা-সংস্করণ--english-version">⬆️ Back to Top / শীর্ষে যান</a>
</div>
