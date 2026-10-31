# Aimi Curtain — Projek Pelanggan Depan Badlishah (TikTok / Reels)

`preview_v1.mp4` — 1080×1920, 30fps, 43.4s. **Belum final export.**

Pelanggan bercakap sekejap (9s), jadi video dibina sebagai cerita projek menggunakan SEMUA footage & gambar:
tiba di rumah → pemasangan (penjejak Ukur ✓ Jahit ✓ Pasang ✓ Kemaskan ✓ Siap) → hasil siap (ruang tamu, setiap sudut,
dapur) → testimoni pelanggan dengan teks kinetik penuh → end card. Konsep Gold Kinetic Luxe sama seperti siri sebelum.

## Struktur
- `src/timeline.json` — segmen footage/gambar, testimoni, beat teks, animasi, SFX.
- `src/Viz.tsx` — penjejak langkah, tag ruang, kad iklan + pin "orang tempatan", bintang.
- `src/Main.tsx` — susunan, framing testimoni (crop sari kata asal), end card.
- `audio/build_audio.py` — muzik (lebih kuat semasa montaj, duck semasa testimoni) & SFX.
