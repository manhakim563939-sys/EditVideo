# EditVideo

`output/vox_style_edit.mp4` — klip asal (VID-20260928-WA0017) dengan background dibuang dan diedit semula gaya Vox:
latar kertas bertekstur + grid, subjek sebagai potongan "sticker" bergaris putih, kad tajuk animasi,
diagram (ikon orang, carta duit menurun, garis masa 2 tahun, kiraan RM), cop "TETAP PEMBAZIRAN", dan sari kata.

`vox_render.py` — skrip render (perlukan frame 30fps + mask `rembg u2net_human_seg` + font Google).

## Aimi Curtain — `output/aimi_curtain_vox.mp4`

Video penerangan langsir (VID-20260925-WA0007) yang background-nya dibuang dan diedit semula gaya Vox (1080x1920, 46s):
subjek sebagai potongan "sticker" atas latar kertas, kad tajuk animasi, swatch warna DULU→SEKARANG, cop KUSAM/SEGAN,
kesan "suram" hitam-putih → REFRESH!, logo Aimi Curtain, B-roll pemasangan (VID-20260928-WA0005/0007, VID-20260929-WA0028)
sebagai polaroid, langkah UKUR → JAHIT → PASANG, swatch koleksi warna, 4 screenshot testimoni pelanggan,
gambar pelanggan, cop 100% BUMIPUTERA, lokasi Kelang Lama Square Kulim, butang WhatsApp, sari kata dan kesan bunyi.

- `aimi_vox_render.py` — skrip render (frame 30fps + mask `rembg u2net_human_seg` digabung mask MediaPipe selfie
  supaya langsir gelap di belakang tidak ikut terpotong).
- `sfx_mix.py` — jana kesan bunyi (pop, swoosh, cop, ding) mengikut cue `sfx.json` dari render.
