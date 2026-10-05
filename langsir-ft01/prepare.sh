#!/usr/bin/env bash
# Regenerate audio stems after editing src/timeline.json.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q numpy scipy soundfile; }
ffmpeg -v error -y -i public/footage.mp4 -vn -af "highpass=f=75,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -ac 2 public/dialog.wav
.venv/bin/python audio/gen_audio.py
