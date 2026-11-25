---
name: rea-video
description: Trigger ONLY when the user says "rea", "rea koro", "ei video te rea koro", "rea-video", or explicitly asks to reverse-engineer/remake a video (scripts, styles, AI prompts). Do NOT use for general video summaries ("এই ভিডিওতে কী বলেছে?", "সামারি দাও")—those belong to video-content-analyzer. Token-efficient, zero-heat dual-mode video reverse engineering with mandatory confirmation questions.
---

# rea-video (Token-Saver & Zero-Heat Edition)

**Trigger Rule:** Activate this skill **ONLY** when the user explicitly uses phrases like **"rea"**, **"rea koro"**, **"ei video te rea koro"**, **"rea-video"**, or asks to reverse-engineer/remake a video's production style, script, or AI prompts. (Keep strictly separate from `video-content-analyzer` which handles general dialogue summaries and repo/code extraction).

You are an expert video reverse-engineer. Your job is to dissect how a video was made and provide actionable outputs (remake scripts, visual style guides, AI generation prompts, editing/caption breakdowns, audio/BPM, and full `VIDEO.md` style blueprints) **while strictly minimizing token usage and avoiding heavy local CPU/phone heat**.

---

## 🛑 MANDATORY STEP 1: Interactive Question Gate (NEVER SKIP)

Whenever the user shares a video (URL or local file path) and asks to analyze, reverse-engineer, or remake it, **DO NOT process the video or run any heavy extraction immediately**.

You **MUST** first use the `ask_question` tool to force the user to specify their exact requirements:

1. **Time Range Selection:**
   - Question: *"ভিডিওটির কতটুকু অংশ নিয়ে কাজ করতে চান? (টোকেন বাঁচাতে নির্দিষ্ট সময় যেমন `00:00-00:15` দিলে সবচেয়ে ভালো হয়)"*
   - Options:
     - `প্রথম ১৫ সেকেন্ড (00:00 - 00:15) (Recommended)`
     - `প্রথম ৩০ সেকেন্ড (00:00 - 00:30)`
     - `কাস্টম সময় (আমি নিচে লিখে দিচ্ছি)`
     - `পুরো ভিডিও`

2. **Target Outputs (`rea-video` Capabilities - Multi-Select):**
   - Question: *"এই ভিডিও থেকে আপনি কী কী বের করতে চান?"* (set `is_multi_select: true`)
   - Options:
     - `সিন দেখে রিম্যাক স্ক্রিপ্ট ও ডায়ালগ তৈরি`
     - `ভিজ্যুয়াল স্টাইল, কালার গ্রেডিং, লাইটিং ও ক্যামেরা অ্যাঙ্গেল`
     - `AI ভিডিও জেনারেশন প্রম্পট (Runway / Kling / Luma-এর জন্য)`
     - `ক্যাপশন স্টাইল, ফন্ট ও এডিটিং/কাটিং রিদম`
     - `অডিও, ব্যাকগ্রাউন্ড মিউজিক (BPM) ও সাউন্ড ইফেক্ট`

3. **Output Depth (Token Optimization):**
   - Question: *"আউটপুটের ধরন কেমন হবে?"*
   - Options:
     - `অতি সংক্ষিপ্ত ও পয়েন্ট-টু-পয়েন্ট (সর্বোচ্চ টোকেন সাশ্রয়ী) (Recommended)`
     - `স্ট্যান্ডার্ড রিম্যাক ব্লুপ্রিন্ট (VIDEO.md ফরম্যাট)`

---

## ⚡ STEP 2: Dual-Mode Execution Strategy

After receiving the user's answers, follow the appropriate mode based on the video source:

### 🔵 Mode A: YouTube Fast-Track Mode (For YouTube URLs)
If the input is a **YouTube URL** (`youtube.com` / `youtu.be`):
- **Do NOT** download the video or run local `ffmpeg` / `yt-dlp` unless the user explicitly asks for local frame files.
- Analyze the video directly within the selected **Time Range** using server capabilities, focusing **ONLY** on the **Target Outputs** selected by the user.
- This ensures **0% phone heat** and **minimal token usage**.

### 🟢 Mode B: Local File & Other Social URLs (yt-dlp + FFmpeg Slicer)
If the input is a **local file** (`/sdcard/...`, etc.) or **other URLs** (Facebook, Instagram, X, TikTok, direct MP4):
Run our lightweight helper script `scripts/slice_media.sh` (or direct `yt-dlp` + `ffmpeg` commands) in `$TMPDIR` to extract **only** the requested time range with zero heavy Python ML libraries:

```bash
bash /data/user/0/ai.antigem/files/home/.gemini/config/skills/rea-video/scripts/slice_media.sh "<INPUT_PATH_OR_URL>" "<START_TIME>" "<END_TIME>" "<NEED_AUDIO_BOOL>"
```

- **What it does:**
  1. Uses `yt-dlp -g` (if URL) to get the direct stream without downloading the full file.
  2. Uses `ffmpeg -ss <start> -to <end>` to extract **only** the target clip.
  3. Extracts **scene-change keyframes** (`select='gt(scene,0.35)',scale=640:-1`) so only unique shots are sent to the model (saves 80%+ image tokens).
  4. If audio/BPM/script was requested, extracts a tiny compressed MP3 (`-b:a 48k -ac 1`).
- Inspect the extracted frames and audio using your built-in multimodal `read_file` tool, then generate the requested `rea-video` breakdown.

---

## 🎯 STEP 3: Delivering the Output

Structure your final response strictly around what the user selected in **Step 1**:
- **Production Type:** Briefly state whether shots are Live Action, AI-generated, 3D, Code Render (e.g., Remotion), or Mixed.
- **Selected Deliverables:** Provide the exact Script, Style/Lighting, AI Prompts, Captions, or Audio breakdown requested.
- **Cleanup:** Mention the temporary directory in `$TMPDIR` if any local slices were created so the user knows no storage was wasted.
