#!/usr/bin/env bash
# Build the preview: visuals + procedural audio + mix -> output/preview_aimi_curtain.mp4
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt; }
DUR=$($PY -c "import sys; sys.path.insert(0,'src'); import timeline; print(timeline.DURATION)")
DEND=$($PY -c "import sys; sys.path.insert(0,'src'); import timeline; print(timeline.DIALOGUE_END)")

$PY src/audio.py
[ "${MIX_ONLY:-0}" = 1 ] || $PY src/render.py

# Dialogue: original speech untouched in timing/speed, only loudness-normalised.
# Music is side-chain ducked by the dialogue and lifted for the end card;
# SFX sit on top; final limiter at -1 dBFS.
ffmpeg -v error -y -i build/video.mp4 -i assets/source/talking_head.mp4 -i build/music.wav -i build/sfx.wav \
  -filter_complex "\
[1:a]aresample=48000,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,apad,atrim=0:${DUR},asplit=2[dlg][key];\
[2:a]volume=0.35[mus];\
[mus][key]sidechaincompress=threshold=0.05:ratio=2.5:attack=15:release=450:makeup=1,volume='if(gte(t,${DEND}),2.0,1)':eval=frame[mduck];\
[3:a]volume=0.55[fx];\
[dlg][mduck][fx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.891:level=disabled[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -t "${DUR}" -movflags +faststart \
  output/preview_aimi_curtain.mp4
echo "done: output/preview_aimi_curtain.mp4"
