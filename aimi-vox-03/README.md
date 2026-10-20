# Aimi Curtain — Vox × Kinetic Typography Edit #3 (TikTok / Reels)


**FINAL:** `AimiCurtain_Vox03_Final_9x16.mp4` — 1080×1920, 30fps, 38.0s, x264 CRF 17 (slow), AAC 256k, −16.8 LUFS.
`preview_v1.mp4` — 1080×1920, 30fps, 38.0s (35.6s video utama 03 + 2.4s end card). **Belum final export.**

Arah visual: **Vox Explainer × Gold Kinetic**. Bahagian penerangan (jimat duit, aircond 16, bil hujung bulan,
kain tebal sekat haba/cahaya) jadi kolaj gaya Vox atas kertas bertekstur dengan host sebagai foto bertampal,
label taip, highlighter dan bulatan/anak panah merah. Bahagian bercakap guna teks kinetik Montserrat emas.
Overlay berkaitan: foto langsir siap Aimi Curtain (beranotasi) dan B-roll ruang tamu yang menjadi redup/sejuk.

## Struktur
- `src/timeline.json` — segmen (th / vox / photos / room), jump-zoom, teks Vox, beat kinetik, SFX.
- `src/Vox.tsx` — kertas, host card, headline highlighter, diagram (money, aircond, bill, sun), kolaj foto, ruang tamu.
- `src/Kinetic.tsx`, `src/Fx.tsx` — teks kinetik & animasi (dikongsi dengan edit #2).
- `src/Main.tsx` — susunan segmen, end card, audio. `audio/build_audio.py` — muzik & SFX procedural.

## Render
```bash
npm install
.venv/bin/python audio/build_audio.py
npx remotion render src/index.ts Main out/video.mp4 --crf=18
```
