# Aimi Curtain — Review Pelanggan Taman Kedidi (TikTok / Reels)


**FINAL:** `AimiCurtain_TamanKedidi_Final_9x16.mp4` — 1080×1920, 30fps, 63.3s, CRF 17, AAC 256k.
`preview_v1.mp4` — 1080×1920, 30fps, 63.3s (60.9s testimoni + 2.4s end card). **Belum final export.**

Konsep sama dengan siri sebelum ini (Gold Kinetic Luxe): teks kinetik emas untuk setiap point pelanggan, animasi
(bintang 5, kad "Kata Pelanggan", harga → OKEY!, keluarga setuju, kontrak habis → masih datang, WORTH IT,
SAYA REKOMEN!) dan B-roll dalam rumah sahaja (bidai zebra, langsir siap, laras bidai). Sari kata asal di atas
video dibuang dengan crop/zoom.

## Struktur
- `src/timeline.json` — framing syot, jump-cut, sisipan B-roll, beat teks, animasi, SFX.
- `src/Viz.tsx` — animasi testimoni. `src/Kinetic.tsx` — teks kinetik. `src/Main.tsx` — susunan & end card.
- `audio/build_audio.py` — muzik & SFX procedural, duck di bawah suara pelanggan.

## Render
```bash
npm install
.venv/bin/python audio/build_audio.py
npx remotion render src/index.ts Main out/video.mp4 --crf=18
```
