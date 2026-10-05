# Firea Celeste Musk — Motion Ad (Awareness–Edutainment) · PREVIEW

9:16 · 1080×1920 · 30fps · 30s · 100% motion, text-led (tiada VO).
Final: `out/Firea_CelesteMusk_9x16_FINAL.mp4` (H.264 yuv420p, CRF 16, AAC 320k, faststart) — `npm run final`.
Preview: `out/firea_preview.mp4`.

## Flow (frame @30fps, dalam `src/timeline.json`)
| Babak | Frame | Isi |
|---|---|---|
| Hook | 0–120 | "Bertudung & berlengan panjang" + foto + sticker Aktif seharian / Banyak bergerak / Banyak berpeluh |
| Persoalan | 120–240 | "Kenapa ketiak tetap berbau? walaupun peluh tak nampak di sebalik lengan baju" |
| Penerangan | 240–480 | 01 peluh hampir tak berbau → 02 bakteria memecahkan peluh → 03 tudung & lengan panjang = kurang aliran udara |
| Penerangan 2 | 480–600 | Deodorant = kawal bau, Antiperspirant = kurangkan peluh → pilih yang buat kedua-duanya |
| Contoh | 600–780 | Firea Celeste Musk + ciri dari label; 50ml mudah dibawa; sesuai kegunaan harian |
| Takeaway | 780–900 | "Kawal peluh, kawal bau — yakin seharian." + logo + CTA "Dapatkan Sekarang" |

## Struktur
- `assets/original/` — salinan bahan asal (tidak diubah)
- `scripts/prep_assets.py` — crop foto, potongan botol (rembg), logo → `public/`
- `scripts/make-audio.mjs` — soundtrack + SFX procedural (120 BPM, F major) → `public/audio/`
- `src/timeline.json` — SATU sumber timing untuk visual & audio
- `src/theme.ts` — warna, font, **teks CTA**
- `src/FireaAd.tsx`, `src/kit.tsx` — babak & komponen motion

## Jalankan
```bash
npm install
python3 -m venv .venv && .venv/bin/pip install "rembg[cpu]" pillow numpy   # hanya jika mahu jana semula aset
.venv/bin/python scripts/prep_assets.py
npm run audio      # jana semula audio selepas ubah timeline.json
npm run studio     # edit secara visual
npm run preview    # render out/firea_preview.mp4
```
