# Aimi Curtain — VGC-FT01 (Edit Footage · Fast Track)

`preview_v2.mp4` — preview 1080×1920, 30fps, 47.8s (44.9s rakaman asal + 2.9s end card). **Belum final export.**

v2: saat 16.1–30.0 (bahagian tengok phone) ditutup sepenuhnya dengan B-roll pemasangan/hasil + testimoni WhatsApp pelanggan; suara asal kekal.

## Struktur
- `src/timeline.json` — SEMUA timing: shot, punch-in, sari kata, kad grafik, SFX. Visual dan audio baca fail yang sama.
- `src/Main.tsx` — footage, grade (sejuk → hangat), curtain wipe, susun layer & audio.
- `src/Captions.tsx`, `src/Cards.tsx`, `src/EndCard.tsx`, `src/theme.ts` (warna & font).
- `audio/gen_audio.py` — soundtrack + SFX procedural (numpy), ducking ikut dialog.
- `public/footage.mp4` — salinan rakaman asal (bahan asal tidak diubah).
- `public/broll/`, `public/img/` — salinan B-roll & foto ruang tamu. Susunan B-roll dalam `broll` di `src/timeline.json`.

## Cara edit & render
```bash
npm install
./prepare.sh                       # jana semula dialog.wav, music.wav, sfx.wav
npx remotion studio                # pratonton dalam browser
npx remotion render src/index.ts Main out/preview.mp4 --crf=20
```
(Dalam sesi cloud ini: tambah `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`.)
