#!/usr/bin/env bash
# Render frame terpilih ke scratch/stills untuk semakan layout: scripts/stills.sh 20 100 180 ...
BR=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
mkdir -p scratch/stills
for fr in "$@"; do
  npx remotion still FireaAd "scratch/stills/f$fr.png" --frame="$fr" --browser-executable="$BR" --log=error
done
