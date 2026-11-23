# Video Analyzer Tool 🎬⚡

**Video Analyzer Tool** হলো একটি ফাস্ট ও অপ্টিমাইজড ভিডিও ইন্টেলিজেন্স ও স্পিচ অ্যানালাইসিস স্ক্রিপ্ট। এটি পুরো ভিডিও ডাউনলোড না করেই রিমোট স্ট্রিমিং লিঙ্ক (Facebook, YouTube, direct URL) বা লোকাল ভিডিও ফাইল থেকে ভয়েস ট্রান্সক্রিপশন, সাইলেন্স ট্রিম, টাইমস্ট্যাম্প রিম্যাপিং এবং গুরুত্বপূর্ণ ভিজ্যুয়াল ফ্রেম ক্যাপচার করতে পারে।

---

## 🌟 প্রধান বৈশিষ্ট্যসমূহ (Features)

1. **জিরো-ডাউনলোড স্ট্রিমিং অ্যানালাইসিস (Zero Full Download)**:
   - গিগাবাইট সাইজের পুরো ভিডিও ডাউনলোড করার প্রয়োজন নেই।
   - `yt-dlp` এবং `ffmpeg` ব্যবহার করে সরাসরি রিমোট অডিও/ভিডিও স্ট্রিম থেকে কাজ করে।
2. **স্মার্ট সাইলেন্স ট্রিমিং (Silence Trimming & Boundary Padding)**:
   - কথার মাঝখানের অতিরিক্ত নীরবতা বাদ দিয়ে প্রসেসিং টাইম ও মেমরি কমায়।
   - স্পিচ বাউন্ডারিতে সেফ প্যাডিং থাকায় কোনো শব্দের শুরু বা শেষ কেটে যায় না।
3. **ওভারহিটিং রোধ ও স্পিড প্রোবিং (Smart Speed Probing)**:
   - লম্বা ভিডিওর ক্ষেত্রে বারবার একাধিক স্পিডে পুরো ফাইল না চালিয়ে ৬০ সেকেন্ডের ছোট স্যাম্পল টেস্ট করে দ্রুততম ও সেরা অ্যাকুরেট স্পিড বেছে নেয়।
4. **অটো টাইমস্ট্যাম্প রিম্যাপিং (Timestamp Remapping)**:
   - স্পিচ ট্রিমিং হওয়ার পরও সাবটাইটেল এবং ফ্রেমের টাইমস্ট্যাম্প স্বয়ংক্রিয়ভাবে মূল ভিডিওর আসল টাইমলাইনের সাথে নিখুঁতভাবে সমন্বয় (remap) হয়।
5. **টার্গেটেড ফ্রেম ক্যাপচার (Targeted Frame Capture)**:
   - ট্রান্সক্রিপ্টে উল্লেখিত গুরুত্বপূর্ণ কি-ওয়ার্ড (যেমন: GitHub repo, link, tool, code, website) শনাক্ত করে স্বয়ংক্রিয়ভাবে সেই মুহূর্তের স্ক্রিনশট ফ্রেম সেভ করে।
6. **বহুভাষিক সমর্থন (Multilingual Support)**:
   - ইংরেজি, বাংলা ও মিশ্র ভাষা (Banglish) নিখুঁতভাবে শনাক্ত ও ট্রান্সক্রাইব করতে পারে।

---

## 📋 প্রয়োজনীয় ডিপেন্ডেন্সি (Prerequisites)

এই টুলটি টার্মাক্স (Android Termux) বা যেকোনো লিনাক্স এনভায়রনমেন্টে চলার উপযোগী।

- **Python 3.8+**
- **FFmpeg & FFprobe**
- **yt-dlp**
- **whisper.cpp** ও মডেলসমূহ (`ggml-large-v3-turbo-q5_0.bin`, `ggml-base.bin`, `ggml-bn-medium-q5_0.bin`)

---

## 🚀 ইন্সটলেশন ও সেটআপ (Installation)

### ১. অটোমেটিক সেটআপ (প্রস্তাবিত)

রিপোজিটরিটি ক্লোন করার পর এক ক্লিকেই ডিপেন্ডেন্সি ও মডেল সেটআপ করতে রান করুন:

```bash
chmod +x install.sh
./install.sh
```

### ২. ম্যানুয়াল সেটআপ (Manual Setup)

যদি ম্যানুয়ালি সেটআপ করতে চান:

```bash
# ১. সিস্টেম প্যাকেজ ইন্সটল
pkg install python ffmpeg -y    # Termux
# অথবা: sudo apt install python3 ffmpeg -y   # Ubuntu/Debian

# ২. yt-dlp ইন্সটল
pip install -U yt-dlp

# ৩. মডেল ফোল্ডার তৈরি ও মডেল ডাউনলোড
mkdir -p "$HOME/tools/whisper.cpp/models"
cd "$HOME/tools/whisper.cpp/models"

# Turbo Model (~574MB)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin

# Base Model (~148MB - ল্যাঙ্গুয়েজ ডিটেকশনের জন্য)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin

# ৪. স্ক্রিপ্টটি এক্সিকিউটেবল করে PATH-এ লিঙ্ক করুন
chmod +x video_analyzer.py
cp video_analyzer.py $PREFIX/bin/video-analyzer   # Termux
# অথবা: sudo cp video_analyzer.py /usr/local/bin/video-analyzer  # Linux
```

---

## 📖 ব্যবহার বিধি (User Manual & Examples)

### বেসিক কমান্ড:
```bash
video-analyzer "<ভিডিও_লিঙ্ক_বা_ফাইল_পাথ>"
```

### বাস্তব উদাহরণ:

1. **অনলাইন ফেসবুক ভিডিও / রিল অ্যানালাইসিস:**
   ```bash
   video-analyzer "https://www.facebook.com/share/v/1DUg7LdCX4/"
   ```

2. **ইউটিউব ভিডিও বা শর্টস অ্যানালাইসিস:**
   ```bash
   video-analyzer "https://youtube.com/shorts/vmD2IHFSutY"
   ```

3. **লোকাল মেমরি/স্টোরেজের ভিডিও ফাইল:**
   ```bash
   video-analyzer "/sdcard/Download/tutorial_video.mp4"
   ```

4. **আউটপুট ফোল্ডার নির্দিষ্ট করে দেওয়া:**
   ডিফল্টভাবে আউটপুট `$HOME/.antigem/media_analysis/` ফোল্ডারে সেভ হয়। আপনি চাইলে নিজস্ব পাথ দিতে পারেন:
   ```bash
   video-analyzer "https://youtube.com/watch?v=..." -o "./output_folder"
   ```

---

## 📂 আউটপুট ফাইলের কাঠামো (Output Structure)

প্রতিটি ভিডিও প্রসেস হওয়ার পর একটি ইউনিক রান ফোল্ডার তৈরি হয়:

```text
media_analysis/<source_hash>_<timestamp>/
├── analysis_manifest.json          # মেটাডাটা, টাইমস্ট্যাম্প ম্যাপিং ও সামারি
├── transcript_clean.txt            # পরিষ্কার ও ডুপ্লিকেশন মুক্ত টেক্সট
├── whisper_sub_original_timeline.srt # মূল ভিডিও টাইমলাইনের সাথে সিঙ্ক করা সাবটাইটেল
├── audio_1p25x_16k_mono.wav        # প্রসেস করা অপ্টিমাইজড অডিও
└── frames/                         # ভিডিওতে দেখানো কি-মোমেন্টের স্ক্রিনশট ফ্রেম
    ├── frame_1_15s_direct.jpg
    └── frame_2_45s_segment.jpg
```

---

## 🔒 লাইসেন্স (License)

ব্যক্তিগত ও ওপেন-সোর্স ব্যবহারের জন্য উন্মুক্ত।
