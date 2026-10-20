# Aimi Curtain — Siri QnA (5 video pendek, TikTok / Reels)

Dipotong daripada satu video temubual (6:45). Suara penyoal **dibuang**; soalan dipaparkan sebagai bubble teks
di awal setiap video (4s), diikuti jawapan Aimi yang dipendekkan (jump-cut), teks kinetik emas dan animasi
penerangan, dan end card WhatsApp.

| Video | Topik | Jawapan | Jumlah |
|---|---|---|---|
| QnA1 | Isu Bajet | 40.5s | 46.8s |
| QnA2 | Tak Pandai Ukur | 49.2s | 55.5s |
| QnA3 | Rumah Panas (material) | 51.5s | 57.8s |
| QnA4 | Tempoh Siap | 17.6s | 23.9s |
| QnA5 | Design & Konsep | 27.3s | 33.6s |

## Struktur
- `spec/spec.json` — SUMBER: segmen yang disimpan (masa video asal), soalan, beat teks, animasi.
- `audio/prep.py <sumber.mp4>` — potong & sambung segmen → `public/qN/clip.mp4`, `public/qN/dialog.wav`, `src/data/qN.json`.
- `audio/build_audio.py qN` — muzik & SFX procedural per video.
- `src/QnA.tsx` — pembuka soalan, jawapan (jump-zoom), end card. `src/Viz.tsx` — animasi penerangan.
- `src/Kinetic.tsx` — teks kinetik.

## Render
```bash
npm install
for q in q1 q2 q3 q4 q5; do .venv/bin/python audio/build_audio.py $q; done
npx remotion render src/index.ts QnA1 out/QnA1.mp4 --crf=18   # QnA1..QnA5
```
