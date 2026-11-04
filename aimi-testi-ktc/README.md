# Aimi Curtain — Review Pelanggan KTC 02 (TikTok / Reels)

`preview_v6.mp4` — 1080×1920, 30fps, 37.1s (34.7s suara pelanggan + 2.4s end card). **Belum final export.**

Video utama tidak menunjukkan muka pelanggan (kamera merakam bilik semasa pemasangan), jadi suara pelanggan
menjadi jalan cerita: teks kinetik untuk setiap ayat, B-roll pemasangan & langsir siap, animasi (jam 2–3 jam,
garis laju, lencana produk/jahitan berkualiti, swatch pilihan, meter Bumi → Langit, bintang), dan split screen
"SANA: KAYANGAN / SINI: MARHAEN". End card: B-roll langsir penuh skrin + animasi logo, percikan emas, "Jom, Aimi Curtain bantu!" (tiada butang WhatsApp).

## Struktur
- `src/timeline.json` — segmen (B-roll / gambar / video utama / split), beat teks, animasi, SFX.
- `src/Viz.tsx` — animasi. `src/Main.tsx` — susunan, split screen, end card. `src/Kinetic.tsx` — teks kinetik.
- `audio/build_audio.py` — muzik & SFX procedural, duck di bawah suara pelanggan.

v3: dari 0:30 hingga akhir hanya B-roll penuh skrin dengan suara pelanggan (tiada teks/animasi/end card).
v4: semua footage/gambar langsir maroon-emas (ruang tamu bersofa) dibuang kerana bukan pemasangan Aimi; diganti dengan langsir krim/beige.
v5: end card hijau dikembalikan dengan CTA "Jom, Aimi Curtain bantu anda!".
v6: sari kata kinetik ditambah semula 30–34.7s; tajuk "Dari bumi ke langit" dibuang dari end card.
