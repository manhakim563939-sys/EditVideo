#!/usr/bin/env bash
# Build the preview: assets -> audio stems -> picture -> mix + mux.
# Usage: ./build.sh [python]   (python must have numpy, opencv-python-headless, pillow)
set -euo pipefail
cd "$(dirname "$0")"
PY=${1:-python3}
mkdir -p build output
$PY scripts/prep_assets.py .
$PY scripts/make_audio.py . build
$PY scripts/render_video.py . build/picture.mp4
# Mix: dialog leads; music/SFX sit under it (already ducked in make_audio.py).
ffmpeg -v error -y -i build/voice.wav -i build/music.wav -i build/sfx.wav -filter_complex "\
[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3dB,volume=1.0[v];\
[1:a]volume=0.19[m];\
[2:a]volume=0.30[s];\
[v][m][s]amix=inputs=3:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]" \
  -map "[a]" -c:a pcm_s16le build/mix.wav
ffmpeg -v error -y -i build/picture.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart output/preview.mp4
echo "done -> output/preview.mp4"
