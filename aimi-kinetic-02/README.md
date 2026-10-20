# Aimi Curtain — Kinetic Typography Edit #2 (TikTok / Reels)


**FINAL:** `AimiCurtain_Kinetic02_Final_9x16.mp4` — 1080×1920, 30fps, 38.2s, CRF 18, AAC 256k, −16.4 LUFS.
`preview_v1.mp4` — 1080×1920, 30fps, 38.2s (36.0s video utama 02 + 2.2s end card). **Belum final export.**

Konsep sama seperti `aimi-kinetic/` (Gold Kinetic Luxe), tetapi overlay foto/video dikurangkan (2 sisipan sahaja)
dan lebih banyak teks kinetik + animasi grafik: kunci & rumah, BLURR, kad soalan, carian Google, lencana logo,
swatch, langkah Ukuran→Jahitan→Pemasangan, kaunter 100%, pin lokasi, butang WhatsApp, jump-zoom setiap ayat.

## Struktur
- `src/timeline.json` — jump-zoom, beat teks (+ `fx`), sisipan, SFX.
- `src/Kinetic.tsx` — enjin teks kinetik. `src/Fx.tsx` — animasi grafik setiap beat.
- `src/Main.tsx` — video utama, sisipan, end card, audio.
- `audio/build_audio.py` — muzik & SFX procedural, duck di bawah dialog.

## Render
```bash
npm install
.venv/bin/python audio/build_audio.py
npx remotion render src/index.ts Main out/video.mp4 --crf=18
```
