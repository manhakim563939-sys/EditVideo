# EditVideo

`output/vox_style_edit.mp4` — klip asal (VID-20260928-WA0017) dengan background dibuang dan diedit semula gaya Vox:
latar kertas bertekstur + grid, subjek sebagai potongan "sticker" bergaris putih, kad tajuk animasi,
diagram (ikon orang, carta duit menurun, garis masa 2 tahun, kiraan RM), cop "TETAP PEMBAZIRAN", dan sari kata.

`vox_render.py` — skrip render (perlukan frame 30fps + mask `rembg u2net_human_seg` + font Google).

`lwp_recap.py` — recap ~5 minit perjalanan Laser Wood Photo: gabung video panjang (slideshow expo, pasukan, family day),
klip pendek booth, dan 24 gambar (Ken Burns, latar kabur untuk potret), dengan tajuk bab dan lagu latar asal.
Hasil (298s, 1280x720) dimuat naik ke folder Drive asal sebagai `LWP_Recap_5min.mp4`.
