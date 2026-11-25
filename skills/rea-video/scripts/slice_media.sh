#!/data/user/0/ai.antigem/files/usr/bin/bash
# Lightweight zero-heat media slicer for rea-video
# Usage: slice_media.sh <input_url_or_file> <start_time> <end_time> <extract_audio:true|false>

set -e

INPUT="$1"
START="${2:-00:00:00}"
END="${3:-00:00:15}"
NEED_AUDIO="${4:-false}"

OUT_DIR="${TMPDIR:-/data/user/0/ai.antigem/files/usr/tmp}/rea_video_slice_$(date +%s)"
mkdir -p "$OUT_DIR/frames"

STREAM_URL="$INPUT"
if [[ "$INPUT" == http* ]]; then
    if command -v yt-dlp >/dev/null 2>&1; then
        STREAM_URL=$(yt-dlp --extractor-args "youtube:player_client=android,web" -f "best[height<=720]/best" -g "$INPUT" | head -n 1)
    fi
fi

# 1. Extract lightweight scene-change keyframes (max 640px width to save vision tokens)
if [ "$END" = "full" ] || [ -z "$END" ]; then
    ffmpeg -y -i "$STREAM_URL" -vf "select='gt(scene,0.35)',scale=640:-1" -fps_mode vfr "$OUT_DIR/frames/shot_%03d.jpg" -loglevel error
else
    ffmpeg -y -ss "$START" -to "$END" -i "$STREAM_URL" -vf "select='gt(scene,0.35)',scale=640:-1" -fps_mode vfr "$OUT_DIR/frames/shot_%03d.jpg" -loglevel error
fi

# Fallback: if no scene change detected (e.g. single static shot), extract 1 fps
if [ -z "$(ls -A "$OUT_DIR/frames")" ]; then
    if [ "$END" = "full" ] || [ -z "$END" ]; then
        ffmpeg -y -i "$STREAM_URL" -vf "fps=1,scale=640:-1" -fps_mode vfr "$OUT_DIR/frames/shot_%03d.jpg" -loglevel error
    else
        ffmpeg -y -ss "$START" -to "$END" -i "$STREAM_URL" -vf "fps=1,scale=640:-1" -fps_mode vfr "$OUT_DIR/frames/shot_%03d.jpg" -loglevel error
    fi
fi

# 2. Extract lightweight mono audio if requested
if [ "$NEED_AUDIO" = "true" ]; then
    if [ "$END" = "full" ] || [ -z "$END" ]; then
        ffmpeg -y -i "$STREAM_URL" -vn -ac 1 -b:a 48k "$OUT_DIR/audio.mp3" -loglevel error || true
    else
        ffmpeg -y -ss "$START" -to "$END" -i "$STREAM_URL" -vn -ac 1 -b:a 48k "$OUT_DIR/audio.mp3" -loglevel error || true
    fi
fi

echo "SLICE_DIR=$OUT_DIR"
ls -lh "$OUT_DIR/frames"
