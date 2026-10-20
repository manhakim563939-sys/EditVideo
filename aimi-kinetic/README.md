# Aimi Curtain — Kinetic Typography Edit (TikTok / Reels)

`preview_v1.mp4` — 1080×1920, 30fps, 35.3s (33.1s video utama + 2.2s end card). **Belum final export.**

Arah visual: **Gold Kinetic Luxe** — zamrud & emas dari logo AIMI CURTAIN; Montserrat Black untuk teks kinetik
(kata kunci emas), Cinzel untuk jenama. Setiap frasa dialog dipaparkan sebagai teks kinetik (berfungsi sebagai sari kata).

## Struktur
- `src/timeline.json` — SEMUA timing: shot asas (video utama / B-roll / gambar / kad jenama / testimoni), beat teks kinetik, PiP, SFX.
- `src/Kinetic.tsx` — enjin teks kinetik (`*perkataan*` = emas; gaya: stamp, badge, swatch, cta, step).
- `src/Main.tsx` — shot, kad jenama, cascade testimoni + kaunter 500+, PiP, end card, audio.
- `audio/build_audio.py` — muzik & SFX procedural, duck di bawah dialog.
- `public/` — proxy H.264 (video utama + B-roll), dialog dinormalkan (−16 LUFS), logo, foto kedai, testimoni.

## Edit & render
```bash
npm install
.venv/bin/python audio/build_audio.py   # selepas ubah sfx/timing (perlu numpy scipy soundfile)
npx remotion studio
npx remotion render src/index.ts Main out/video.mp4 --crf=18
```
