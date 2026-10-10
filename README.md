# EditVideo

`output/vox_style_edit.mp4` — klip asal (VID-20260928-WA0017) dengan background dibuang dan diedit semula gaya Vox:
latar kertas bertekstur + grid, subjek sebagai potongan "sticker" bergaris putih, kad tajuk animasi,
diagram (ikon orang, carta duit menurun, garis masa 2 tahun, kiraan RM), cop "TETAP PEMBAZIRAN", dan sari kata.

`vox_render.py` — skrip render (perlukan frame 30fps + mask `rembg u2net_human_seg` + font Google).

`output/kolaj_video_marketing.mp4` — video 40s (1080x1920) "Kepentingan video dalam marketing bisnes", gaya kolaj Vox:
selfie dipotong jadi sticker kertas + foto gaya hidup (dari kolaj rujukan) sebagai polaroid bertampal pita,
sari kata bergerak perkataan-demi-perkataan, B-roll grafik (82% trafik, feed telefon berhenti, carta reach & jualan),
zoom punch, peralihan kertas koyak, dan kad CTA "Mula buat video hari ini / Follow". Muzik & SFX disintesis.

- `kolaj_render.py <workdir>` — render frame (perlu `photo.jpg`, `mask_u2net_human_seg.png`, `refs/*.jpg`, `fonts/`).
- `kolaj_audio.py out.wav` — muzik latar 112 BPM + SFX disegerakkan dengan suntingan.
