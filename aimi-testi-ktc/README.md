# Aimi Curtain — Review Pelanggan KTC 02 (TikTok / Reels)

`preview_v2.mp4` — 1080×1920, 30fps, 37.1s (34.7s suara pelanggan + 2.4s end card). **Belum final export.**

Video utama tidak menunjukkan muka pelanggan (kamera merakam bilik semasa pemasangan), jadi suara pelanggan
menjadi jalan cerita: teks kinetik untuk setiap ayat, B-roll pemasangan & langsir siap, animasi (jam 2–3 jam,
garis laju, lencana produk/jahitan berkualiti, swatch pilihan, meter Bumi → Langit, bintang), dan split screen
"SANA: KAYANGAN / SINI: MARHAEN". End card: B-roll langsir penuh skrin + animasi logo, percikan emas, "Jom, Aimi Curtain bantu!" (tiada butang WhatsApp).

## Struktur
- `src/timeline.json` — segmen (B-roll / gambar / video utama / split), beat teks, animasi, SFX.
- `src/Viz.tsx` — animasi. `src/Main.tsx` — susunan, split screen, end card. `src/Kinetic.tsx` — teks kinetik.
- `audio/build_audio.py` — muzik & SFX procedural, duck di bawah suara pelanggan.
