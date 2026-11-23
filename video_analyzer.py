#!/data/user/0/ai.antigem/files/usr/bin/python3
"""video_analyzer.py - Video speech, mapped-timeline transcript, and targeted frame extraction."""
import sys
import os
import re
import json
import subprocess
import argparse
import hashlib
import time
import bisect
from pathlib import Path

MODELS_DIR = "/data/user/0/ai.antigem/files/home/tools/whisper.cpp/models"
MODEL_TURBO = os.path.join(MODELS_DIR, "ggml-large-v3-turbo-q5_0.bin")
MODEL_BN = os.path.join(MODELS_DIR, "ggml-bn-medium-q5_0.bin")
MODEL_BASE = os.path.join(MODELS_DIR, "ggml-base.bin")

KEYWORD_PATTERNS = [
    # English
    r"\brepo\b", r"\brepository\b", r"\bgithub\b", r"\bcode\b", r"\bproject\b",
    r"\btool\b", r"\bwebsite\b", r"\blink\b", r"\bscreen\b", r"\bcheck out\b",
    r"\bdownload\b", r"\binstall\b", r"\bpackage\b", r"\bclone\b",
    # Bangla / Banglish
    r"রেপো", r"রিপো", r"গিটহাব", r"কোড", r"প্রজেক্ট", r"টুল", r"ওয়েবসাইট",
    r"ওয়েবসাইটে", r"লিংক", r"লিংকে", r"স্ক্রিন", r"স্ক্রিনে", r"দেখুন", r"দেখেন",
    r"ক্লোন", r"ইন্সটল", r"প্যাকেজ", r"সফটওয়্যার"
]

def run_cmd(cmd):
    env = os.environ.copy()
    env["PATH"] = f"/data/user/0/ai.antigem/files/usr/bin:{env.get('PATH', '')}"
    env["PREFIX"] = "/data/user/0/ai.antigem/files/usr"
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )
    out, err = p.communicate()
    return p.returncode, out, err

def is_url(target):
    return target.startswith("http://") or target.startswith("https://")

def get_media_metadata(url):
    print("[*] Fetching video metadata and description...")
    cmd = [
        "yt-dlp", "--skip-download", "--dump-single-json",
        "--no-playlist", "--no-warnings", url
    ]
    code, out, _ = run_cmd(cmd)
    if code == 0 and out.strip():
        try:
            data = json.loads(out)
            return {
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "duration": data.get("duration", 0),
                "uploader": data.get("uploader", ""),
                "tags": data.get("tags", []),
                "chapters": data.get("chapters", [])
            }
        except Exception:
            pass
    return {}

def get_stream_urls(url):
    print("[*] Resolving direct media streams (No full download)...")
    _, video_url, _ = run_cmd(["yt-dlp", "-g", "-f", "bestvideo[ext=mp4]/best[ext=mp4]/bestvideo/best", url])
    _, audio_url, _ = run_cmd(["yt-dlp", "-g", "-f", "bestaudio/best", url])
    v_url = video_url.strip().split("\n")[0] if video_url.strip() else ""
    a_url = audio_url.strip().split("\n")[0] if audio_url.strip() else ""
    return v_url, a_url

def try_fetch_online_subtitles(url, out_prefix):
    print("[*] Checking for existing official/auto-generated subtitles...")
    sub_cmd = [
        "yt-dlp", "--skip-download", "--write-auto-sub", "--write-sub",
        "--sub-lang", "bn,en,en-orig,hi,all", "--convert-subs", "srt",
        "--ffmpeg-location", "/data/user/0/ai.antigem/files/usr/bin",
        "-o", f"{out_prefix}.%(ext)s", url
    ]
    code, _, _ = run_cmd(sub_cmd)
    # Check directly converted SRT
    for p in Path(os.path.dirname(out_prefix)).glob(f"{Path(out_prefix).name}*.srt"):
        if p.is_file() and p.stat().st_size > 50:
            print(f"[✓] Online subtitles fetched (SRT): {p.name}")
            return str(p)
    # Check VTT and convert via ffmpeg
    for p in Path(os.path.dirname(out_prefix)).glob(f"{Path(out_prefix).name}*.vtt"):
        if p.is_file() and p.stat().st_size > 50:
            srt_target = str(p).rsplit(".", 1)[0] + ".srt"
            run_cmd(["ffmpeg", "-y", "-i", str(p), srt_target])
            if os.path.isfile(srt_target) and os.path.getsize(srt_target) > 50:
                print(f"[✓] Online subtitles fetched and converted: {Path(srt_target).name}")
                return srt_target
    return None

SILENCE_THRESHOLD_DB = -35
SILENCE_MIN_DURATION = 0.25
MAX_TRIM_SEGMENTS = 400
SPEED_STEPS = [1.25, 1.0, 0.85]
GOOD_TRANSCRIPT_SCORE = 8.0

def probe_duration(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    code, out, _ = run_cmd(cmd)
    try:
        return float(out.strip().splitlines()[0])
    except Exception:
        return None

def detect_silence_ranges(input_src, duration):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", input_src, "-vn",
           "-af", f"silencedetect=noise={SILENCE_THRESHOLD_DB}dB:d={SILENCE_MIN_DURATION}", "-f", "null", "-"]
    _, _, err = run_cmd(cmd)
    ranges, start = [], None
    for line in err.splitlines():
        m = re.search(r"silence_start:\s*(-?[0-9.]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end:\s*([0-9.]+)", line)
        if m and start is not None:
            end = float(m.group(1))
            if end > start:
                ranges.append([start, end])
            start = None
    if start is not None and duration and duration > start:
        ranges.append([start, duration])
    return ranges

def build_kept_intervals(silence_ranges, duration, min_silence_to_cut=0.6, padding=0.08):
    """
    Build intervals of kept audio with speech padding, merging short pauses (< min_silence_to_cut)
    to prevent segment explosion and ensure natural speech boundaries.
    """
    if not silence_ranges:
        return [[0.0, duration]] if duration else []

    # Filter out silences that are too short to warrant a cut (e.g. natural brief pauses in sentence)
    effective_silences = []
    for s, e in silence_ranges:
        s = max(0.0, min(s, duration))
        e = max(s, min(e, duration))
        if (e - s) >= min_silence_to_cut:
            # Leave a little padding for speech boundary
            s_pad = min(duration, s + padding)
            e_pad = max(0.0, e - padding)
            if e_pad > s_pad:
                effective_silences.append([s_pad, e_pad])

    if not effective_silences:
        return [[0.0, duration]] if duration else []

    kept = []
    pos = 0.0
    for s, e in effective_silences:
        if s > pos:
            kept.append([round(pos, 6), round(s, 6)])
        pos = max(pos, e)
    if pos < duration:
        kept.append([round(pos, 6), round(duration, 6)])

    # Further merge adjacent or overlapping intervals
    merged = []
    for start, end in kept:
        if end - start < 0.1:
            continue
        if not merged:
            merged.append([start, end])
        else:
            prev_start, prev_end = merged[-1]
            if start <= prev_end + 0.05:
                merged[-1][1] = max(prev_end, end)
            else:
                merged.append([start, end])
    return merged

def trim_to_kept_intervals(input_src, out_wav, kept, speed=1.0):
    if not kept or len(kept) > MAX_TRIM_SEGMENTS:
        return False, f"segment_count_limit_or_empty ({len(kept) if kept else 0})"
    filters, labels = [], []
    for i, (start, end) in enumerate(kept):
        label = f"seg{i}"
        filters.append(f"[0:a]atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS[{label}]")
        labels.append(f"[{label}]")
    filters.append(f"{''.join(labels)}concat=n={len(kept)}:v=0:a=1[outa]")
    if speed != 1.0:
        filters.append(f"[outa]atempo={speed}[sped]")
        output_label = "[sped]"
    else:
        output_label = "[outa]"
    cmd = ["ffmpeg", "-y", "-i", input_src, "-filter_complex", ";".join(filters), "-map", output_label,
           "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", out_wav]
    code, _, err = run_cmd(cmd)
    if code != 0 or not os.path.isfile(out_wav) or os.path.getsize(out_wav) <= 1000:
        return False, err[-300:]
    return True, None

def map_trim_to_orig(t, kept, speed=1.0):
    if not kept:
        return max(0.0, t) * speed
    t_src = max(0.0, t) * speed
    cum = 0.0
    for index, (a, b) in enumerate(kept):
        length = b - a
        if t_src < cum + length or index == len(kept) - 1:
            return a + min(max(0.0, t_src - cum), length)
        cum += length
    return kept[-1][1]

def extract_audio_wav(input_src, out_wav, speed=1.0, kept=None, silence_ranges=None, source_duration=None):
    print(f"[*] Extracting 16kHz mono audio with mapped silence trimming ({speed}x)...")
    if kept is None:
        source_duration = probe_duration(input_src)
        if not source_duration:
            print("[!] Could not determine source duration; keeping the full audio without trimming.")
            silence_ranges, kept = [], []
        else:
            silence_ranges = detect_silence_ranges(input_src, source_duration)
            kept = build_kept_intervals(silence_ranges, source_duration)
    trimmed, reason = trim_to_kept_intervals(input_src, out_wav, kept, speed)
    if trimmed:
        actual_duration = probe_duration(out_wav)
        predicted_duration = (sum(b - a for a, b in kept) / speed) if speed else None
        drift = abs(actual_duration - predicted_duration) if actual_duration is not None and predicted_duration is not None else None
        mapping = {
            "source_duration": source_duration,
            "trimmed_duration": actual_duration,
            "predicted_trimmed_duration": predicted_duration,
            "duration_drift_seconds": drift,
            "speed": speed,
            "silence_threshold_db": SILENCE_THRESHOLD_DB,
            "silence_min_duration": SILENCE_MIN_DURATION,
            "silence_ranges": [[round(a, 6), round(b, 6)] for a, b in silence_ranges],
            "kept_intervals": [[round(a, 6), round(b, 6)] for a, b in kept],
            "mapping_method": "concatenated_kept_intervals",
            "mapping_approximate": bool(drift is not None and drift > 0.25),
        }
        return True, mapping
    print(f"[!] Deterministic silence trimming unavailable ({reason}); falling back to full audio at {speed}x.")
    cmd_std = ["ffmpeg", "-y", "-i", input_src, "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le"]
    if speed != 1.0:
        cmd_std += ["-af", f"atempo={speed}"]
    cmd_std += [out_wav]
    code, _, err = run_cmd(cmd_std)
    if code != 0 or not os.path.isfile(out_wav):
        print(f"[x] Error extracting 16kHz mono audio: {err[-300:]}")
        return False, None
    return True, {
        "source_duration": source_duration,
        "trimmed_duration": probe_duration(out_wav),
        "predicted_trimmed_duration": source_duration / speed if source_duration else None,
        "duration_drift_seconds": 0.0,
        "speed": speed,
        "silence_threshold_db": SILENCE_THRESHOLD_DB,
        "silence_ranges": [],
        "kept_intervals": [[0.0, source_duration]] if source_duration else [],
        "mapping_method": "untrimmed_source_audio",
        "mapping_approximate": False,
        "trimming_skipped": True,
    }

def detect_language(wav_path):
    print("[*] Detecting speech language...")
    cmd = ["whisper-cli", "-m", MODEL_BASE, "-f", wav_path, "-dl"]
    code, out, err = run_cmd(cmd)
    combined = out + err
    match = re.search(r"detected language:\s*([a-zA-Z]+)", combined, re.IGNORECASE)
    if match:
        lang = match.group(1).lower()
        print(f"[✓] Detected language: {lang}")
        return lang
    print("[!] Language defaulted to 'auto'.")
    return "auto"

def transcribe_with_whisper(wav_path, lang, out_srt_base):
    # Model selection: Turbo is fastest with highest accuracy; fallback to Base or BN
    if os.path.isfile(MODEL_TURBO):
        model = MODEL_TURBO
        chosen_lang = lang if lang in ["bn", "en"] else "auto"
        print(f"[*] Using Large-v3-Turbo model (Fast & Accurate): {Path(model).name}")
    elif lang == "bn" and os.path.isfile(MODEL_BN):
        model = MODEL_BN
        chosen_lang = "bn"
        print(f"[*] Using Bengali model: {Path(model).name}")
    else:
        model = MODEL_BASE
        chosen_lang = lang
        print(f"[*] Using Base lightweight model: {Path(model).name}")
    print(f"[*] Running fast greedy Whisper transcription (-bs 1 -bo 1 -nf)...")
    cmd = [
        "whisper-cli", "-m", model, "-f", wav_path,
        "-l", chosen_lang,
        "-t", "4",
        "-bs", "1", "-bo", "1",
        "-nf",
        "-pp",
        "-osrt", "-of", out_srt_base
    ]
    code, out, err = run_cmd(cmd)
    srt_file = f"{out_srt_base}.srt"
    if os.path.isfile(srt_file):
        print(f"[✓] Transcript generated successfully: {srt_file}")
        return srt_file
    print(f"[x] Whisper transcription failed: {err[-400:]}")
    return None

def parse_srt(srt_path):
    if not srt_path or not os.path.isfile(srt_path):
        return []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    entries = []
    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            time_match = re.match(r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})", lines[1])
            if time_match:
                start_str = time_match.group(1).replace(",", ".")
                end_str = time_match.group(2).replace(",", ".")
                raw_text = " ".join(lines[2:])
                cleaned_text = re.sub(r"<[^>]+>", "", raw_text).strip()
                if cleaned_text:
                    entries.append({
                        "start": start_str,
                        "end": end_str,
                        "text": cleaned_text
                    })
    return entries

def deduplicate_transcript(entries):
    words = []
    normalize = lambda word: re.sub(r"\W+", "", word, flags=re.UNICODE).casefold()
    for item in entries:
        new_words = item["text"].split()
        overlap = 0
        max_overlap = min(len(new_words), len(words), 20)
        for k in range(max_overlap, 0, -1):
            if [normalize(w) for w in words[-k:]] == [normalize(w) for w in new_words[:k]]:
                overlap = k
                break
        words.extend(new_words[overlap:])
    return " ".join(words)

def transcript_quality(entries, lang, duration):
    text = " ".join(item["text"] for item in entries)
    tokens = re.findall(r"[^\W_]+", text, flags=re.UNICODE)
    minimum_words = max(GOOD_TRANSCRIPT_SCORE, int(duration * 0.5))
    if lang == "bn" and tokens:
        script_ratio = sum(bool(re.search(r"[ঀ-৿]", token)) for token in tokens) / len(tokens)
    elif lang == "en" and tokens:
        script_ratio = sum(bool(re.search(r"[A-Za-z]", token)) for token in tokens) / len(tokens)
    else:
        script_ratio = 1.0 if tokens else 0.0
    accepted = len(tokens) >= minimum_words and script_ratio >= 0.35
    return {"words": len(tokens), "minimum_words": minimum_words,
            "script_ratio": round(script_ratio, 3), "accepted": accepted}

def time_str_to_seconds(t_str):
    parts = t_str.split(":")
    h = float(parts[0])
    m = float(parts[1])
    s = float(parts[2].replace(",", "."))
    return h * 3600 + m * 60 + s

def seconds_to_hms(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"

def seconds_to_srt_time(seconds):
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def remap_entries_to_source(entries, kept, speed=1.0):
    """Rewrite SRT entry times from the processed audio to the source video timeline."""
    remapped = []
    for item in entries:
        start = map_trim_to_orig(time_str_to_seconds(item["start"]), kept, speed)
        end = map_trim_to_orig(time_str_to_seconds(item["end"]), kept, speed)
        remapped.append({
            "start": seconds_to_srt_time(start),
            "end": seconds_to_srt_time(max(end, start)),
            "text": item["text"],
        })
    return remapped

def write_srt(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(entries, 1):
            f.write(f"{idx}\n{item['start']} --> {item['end']}\n{item['text']}\n\n")
    return path

def find_key_moments(entries):
    key_moments = []
    regex = re.compile("|".join(KEYWORD_PATTERNS), re.IGNORECASE)
    last_added_sec = -99
    for item in entries:
        if regex.search(item["text"]):
            sec = time_str_to_seconds(item["start"])
            # Keep snapshots at least 15 seconds apart to avoid duplicate images
            if sec - last_added_sec >= 15:
                key_moments.append({
                    "time_sec": sec,
                    "time_str": item["start"],
                    "text": item["text"]
                })
                last_added_sec = sec
    return key_moments

FRAME_SEGMENT_RADIUS = 2.0

def capture_frames(video_src, moments, out_dir, remote_source=None, source_duration=None):
    os.makedirs(out_dir, exist_ok=True)
    captured, skipped = [], []
    if not moments:
        return captured, skipped

    # Refresh remote video URL if expired or remote
    fresh_video_url = video_src
    if remote_source:
        print("[*] Ensuring fresh stream URL for frame extraction...")
        v_url, _ = get_stream_urls(remote_source)
        if v_url:
            fresh_video_url = v_url

    print(f"[*] Extracting {len(moments)} targeted visual frames via FFmpeg...")
    for idx, moment in enumerate(moments[:10]):
        sec = moment["time_sec"]
        hms = seconds_to_hms(sec)
        stem = f"frame_{idx+1}_{int(sec)}s"
        direct_img = os.path.join(out_dir, f"{stem}_direct.jpg")
        code, _, _ = run_cmd(["ffmpeg", "-y", "-ss", hms, "-i", fresh_video_url,
                              "-frames:v", "1", "-q:v", "2", direct_img])
        image_path, method, segment_range = None, None, None
        if code == 0 and os.path.isfile(direct_img) and os.path.getsize(direct_img) > 0:
            image_path, method = direct_img, "direct_stream_frame"
        else:
            start = max(0.0, sec - FRAME_SEGMENT_RADIUS)
            end = min(sec + FRAME_SEGMENT_RADIUS, source_duration) if source_duration else sec + FRAME_SEGMENT_RADIUS
            if source_duration and start <= 0 and end >= source_duration - 0.05:
                skipped.append({"timestamp": hms, "reason": "segment_would_be_full_video_user_approval_required"})
                print(f"[!] A short clip would equal the full video at {hms}; skipping until user approval.")
                continue
            segment = os.path.join(out_dir, f"{stem}_segment.mp4")
            duration = max(0.1, end - start)
            local_cmd = ["ffmpeg", "-y", "-ss", seconds_to_hms(start), "-i", fresh_video_url,
                         "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "ultrafast",
                         "-crf", "30", segment]
            seg_code, _, seg_err = run_cmd(local_cmd)
            if (seg_code != 0 or not os.path.isfile(segment) or os.path.getsize(segment) == 0) and remote_source:
                section = f"*{start:.3f}-{end:.3f}"
                seg_prefix = os.path.join(out_dir, f"{stem}_ytsegment")
                ytdlp_cmd = ["yt-dlp", "--no-warnings", "--no-playlist", "--download-sections", section,
                             "-f", "best[ext=mp4]/best", "--force-overwrites", "-o",
                             seg_prefix + ".%(ext)s", remote_source]
                seg_code, _, seg_err = run_cmd(ytdlp_cmd)
                if seg_code == 0:
                    matches = [p for p in Path(out_dir).glob(f"{stem}_ytsegment.*")
                               if p.is_file() and p.stat().st_size > 0]
                    if matches:
                        segment = str(matches[0])
            segment_duration = probe_duration(segment) if os.path.isfile(segment) else None
            if segment_duration and segment_duration > duration + 3.0:
                skipped.append({"timestamp": hms, "reason": "segment_exceeded_expected_duration_user_approval_required",
                                "segment_duration": round(segment_duration, 3), "expected_duration": round(duration, 3)})
                print(f"[!] Segment at {hms} exceeded the expected short duration; not using it.")
                continue
            if segment_duration:
                relative_sec = min(max(0.0, sec - start), max(0.0, segment_duration - 0.01))
                fallback_img = os.path.join(out_dir, f"{stem}_segment.jpg")
                frame_code, _, _ = run_cmd(["ffmpeg", "-y", "-ss", seconds_to_hms(relative_sec), "-i", segment,
                                            "-frames:v", "1", "-q:v", "2", fallback_img])
                if frame_code == 0 and os.path.isfile(fallback_img) and os.path.getsize(fallback_img) > 0:
                    image_path, method = fallback_img, "short_segment"
                    segment_range = [round(start, 3), round(end, 3)]
                    print(f"  [+] Short segment {start:.1f}s–{end:.1f}s retained: {segment}")
            if not image_path:
                skipped.append({"timestamp": hms, "reason": "direct_and_short_segment_capture_failed"})
                print(f"[!] Short-segment fallback failed at {hms}: {seg_err[-180:]}")
        captured.append({"timestamp": hms, "text_said": moment["text"], "image_path": image_path,
                         "capture_method": method, "segment_range_original_timeline": segment_range})
        print(f"  [+] Captured snapshot at {hms} via {method}: {image_path}")
    return captured, skipped

def probe_speed_quality(audio_src, kept, silence_ranges, source_duration, lang, sample_duration=60.0):
    """
    Evaluate 1.25x vs fallback using a 60-second probe sample to prevent
    repeatedly transcribing full long audio files and overheating the phone.
    """
    print("[*] Probing transcription quality on short sample...")
    sample_kept = []
    for a, b in kept:
        if a >= sample_duration:
            break
        sample_kept.append([a, min(b, sample_duration)])
    if not sample_kept and source_duration:
        sample_kept = [[0.0, min(source_duration, sample_duration)]]

    tmp_probe_wav = f"/data/user/0/ai.antigem/files/usr/tmp/probe_1p25x_{os.getpid()}.wav"
    tmp_probe_srt = f"/data/user/0/ai.antigem/files/usr/tmp/probe_1p25x_{os.getpid()}"
    ok, _ = trim_to_kept_intervals(audio_src, tmp_probe_wav, sample_kept, speed=1.25)
    if not ok:
        if os.path.isfile(tmp_probe_wav):
            try: os.remove(tmp_probe_wav)
            except Exception: pass
        return 1.0

    probe_srt_file = transcribe_with_whisper(tmp_probe_wav, lang, tmp_probe_srt)
    entries = parse_srt(probe_srt_file) if probe_srt_file else []
    probe_dur = probe_duration(tmp_probe_wav) or 30.0
    quality = transcript_quality(entries, lang, probe_dur)

    # Clean up temp probe files
    for p in [tmp_probe_wav, f"{tmp_probe_srt}.srt"]:
        if os.path.isfile(p):
            try: os.remove(p)
            except Exception: pass

    if quality["accepted"] and quality["words"] >= 15:
        print("[✓] Probe test passed: 1.25x speed produces high quality transcript.")
        return 1.25
    else:
        print("[!] Probe test indicated 1.25x may degrade quality; selecting standard 1.0x.")
        return 1.0

def main():
    parser = argparse.ArgumentParser(description="Analyze video speech and visual content quickly without phone overheating")
    parser.add_argument("target", help="Video URL or local file path")
    parser.add_argument("-o", "--outdir", default="/data/user/0/ai.antigem/files/home/.antigem/media_analysis", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    target = args.target
    is_remote = is_url(target)

    run_key = hashlib.sha1(target.encode("utf-8")).hexdigest()[:10]
    run_stamp = time.strftime('%Y%m%d-%H%M%S') + f"-{time.time_ns() % 1_000_000_000:09d}"
    run_dir = os.path.join(args.outdir, f"{run_key}_{run_stamp}")
    os.makedirs(run_dir, exist_ok=True)
    print(f"[*] Run output: {run_dir}")

    metadata = {}
    video_src = target if not is_remote else None
    audio_src = target if not is_remote else None

    if is_remote:
        metadata = get_media_metadata(target)
        if metadata.get("title"):
            print(f"[✓] Title: {metadata['title']}")

    srt_file = None
    timeline_mapping = None

    if is_remote:
        srt_file = try_fetch_online_subtitles(target, os.path.join(run_dir, "online_sub"))

    if not srt_file:
        if is_remote:
            v_url, a_url = get_stream_urls(target)
            audio_src = a_url or v_url
            if not audio_src:
                print("[x] Could not resolve an audio stream from the URL.")
                sys.exit(1)
            video_src = v_url or None

        source_duration = probe_duration(audio_src)
        silence_ranges = detect_silence_ranges(audio_src, source_duration) if source_duration else []
        kept = build_kept_intervals(silence_ranges, source_duration) if source_duration else []

        lang = "auto"
        # Initial quick check of language from raw stream or first sample if possible
        init_wav = os.path.join(run_dir, "audio_init_sample.wav")
        sample_kept = kept[:5] if kept else [[0.0, min(source_duration or 30.0, 30.0)]]
        trimmed_init, _ = trim_to_kept_intervals(audio_src, init_wav, sample_kept, speed=1.0)
        if trimmed_init and os.path.isfile(init_wav):
            lang = detect_language(init_wav)
            try: os.remove(init_wav)
            except Exception: pass

        # Choose speed smartly without multi-pass overhead on long videos
        if source_duration and source_duration > 120.0:
            target_speed = probe_speed_quality(audio_src, kept, silence_ranges, source_duration, lang)
            candidate_speeds = [target_speed]
        else:
            candidate_speeds = SPEED_STEPS

        best_score, best_srt, best_mapping, best_wav, attempts = -1, None, None, None, []
        for speed in candidate_speeds:
            speed_tag = str(speed).replace(".", "p")
            wav_file = os.path.join(run_dir, f"audio_{speed_tag}x_16k_mono.wav")
            extracted, mapping = extract_audio_wav(
                audio_src, wav_file, speed, kept, silence_ranges, source_duration
            )
            if not extracted:
                print(f"[!] Could not prepare audio at {speed}x; trying next speed.")
                attempts.append({"speed": speed, "result": "audio_extraction_failed"})
                continue

            if lang == "auto":
                lang = detect_language(wav_file)

            attempt_srt = os.path.join(run_dir, f"whisper_sub_{speed_tag}x")
            attempt_file = transcribe_with_whisper(wav_file, lang, attempt_srt)
            entries = parse_srt(attempt_file) if attempt_file else []
            processed_duration = probe_duration(wav_file) or 0.0
            quality = transcript_quality(entries, lang, processed_duration)
            score = quality["words"]
            print(f"[*] Transcript quality proxy at {speed}x: {score} words across {len(entries)} cues; script ratio {quality['script_ratio']}.")
            attempts.append({"speed": speed, **quality, "cues": len(entries)})

            if score > best_score and attempt_file:
                best_score, best_srt, best_mapping, best_wav = score, attempt_file, mapping, wav_file

            if quality["accepted"]:
                print(f"[✓] Accepted transcript at {speed}x.")
                break
            print(f"[!] Transcript too short or missing at {speed}x; trying a slower speed.")

        srt_file, timeline_mapping = best_srt, best_mapping
        if timeline_mapping:
            timeline_mapping["speed_attempts"] = attempts
            timeline_mapping["selected_speed"] = timeline_mapping.get("speed", 1.0)
        if srt_file:
            print(f"[*] Processed audio retained at: {best_wav}")

    if not srt_file or not os.path.isfile(srt_file):
        print("[x] No transcript available.")
        sys.exit(1)

    entries = parse_srt(srt_file)
    if timeline_mapping and (not timeline_mapping.get("trimming_skipped") or timeline_mapping.get("speed", 1.0) != 1.0):
        entries = remap_entries_to_source(
            entries, timeline_mapping.get("kept_intervals", []), timeline_mapping.get("speed", 1.0)
        )
        original_srt = os.path.join(run_dir, "whisper_sub_original_timeline.srt")
        write_srt(entries, original_srt)
        srt_file = original_srt

    print(f"[✓] Parsed {len(entries)} subtitle entries.")

    # Save clean readable speech text without rolling repetitions
    clean_speech = deduplicate_transcript(entries)
    clean_txt_path = os.path.join(run_dir, "transcript_clean.txt")
    with open(clean_txt_path, "w", encoding="utf-8") as f:
        f.write(clean_speech)

    key_moments = find_key_moments(entries)
    frames_dir = os.path.join(run_dir, "frames")

    if is_remote and key_moments and not video_src:
        v_url, _ = get_stream_urls(target)
        video_src = v_url or None

    if video_src:
        captured, skipped_frames = capture_frames(
            video_src, key_moments, frames_dir, target if is_remote else None,
            metadata.get("duration")
        )
    else:
        captured, skipped_frames = [], []
        if key_moments:
            print("[!] Transcript contains visual keywords, but no video stream is available; skipping frame capture.")

    summary_json = os.path.join(run_dir, "analysis_manifest.json")
    manifest = {
        "source": target,
        "is_remote": is_remote,
        "metadata": metadata,
        "srt_path": srt_file,
        "clean_transcript_path": clean_txt_path,
        "timeline_mapping": timeline_mapping,
        "transcript_timestamps_reference": "original_video_timeline" if timeline_mapping else "source_subtitle_timeline",
        "transcription_speed_attempts": timeline_mapping.get("speed_attempts", []) if timeline_mapping else [],
        "selected_transcription_speed": timeline_mapping.get("selected_speed") if timeline_mapping else None,
        "timeline_mapping_approximate": bool(timeline_mapping and timeline_mapping.get("mapping_approximate")),
        "total_dialogues": len(entries),
        "visual_moments_count": len(captured),
        "captured_moments": captured,
        "skipped_frame_attempts": skipped_frames
    }

    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "="*50)
    print("FAST ANALYSIS READY")
    print(f"Title: {metadata.get('title', 'N/A')}")
    print(f"Manifest: {summary_json}")
    print(f"Clean Transcript: {clean_txt_path}")
    print(f"Captured Frames: {len(captured)} snapshots in {frames_dir}")
    print("="*50)

if __name__ == "__main__":
    main()
