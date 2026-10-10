# EditVideo

`output/vox_style_edit.mp4` — klip asal (VID-20260928-WA0017) dengan background dibuang dan diedit semula gaya Vox:
latar kertas bertekstur + grid, subjek sebagai potongan "sticker" bergaris putih, kad tajuk animasi,
diagram (ikon orang, carta duit menurun, garis masa 2 tahun, kiraan RM), cop "TETAP PEMBAZIRAN", dan sari kata.

`vox_render.py` — skrip render (perlukan frame 30fps + mask `rembg u2net_human_seg` + font Google).

`output/kolaj_video_marketing.mp4` — video 39s dengan voice-over ElevenLabs (`assets/vo_elevenlabs.mp3`) (1080x1920) "Kepentingan video dalam marketing bisnes", gaya kolaj Vox:
selfie ekspresi (sinis, terkejut, senyum, fikir, tunjuk) jadi sticker kertas hitam putih dramatik yang
masuk dengan animasi hidup (naik, berayun, goyang stop-motion) + doodle (!!, ?, kilauan), foto gaya hidup (dari kolaj rujukan) sebagai polaroid bertampal pita,
sari kata bergerak perkataan-demi-perkataan, B-roll grafik (82% trafik, feed telefon berhenti, carta reach & jualan),
zoom punch, peralihan kertas koyak, dan kad CTA "Mula buat video hari ini / Follow". Muzik & SFX disintesis.

- `kolaj_render.py <workdir>` — render frame (perlu `photo.jpg`, `mask_u2net_human_seg.png`, `expr/{4..8}.jpg` + `_mask.png`, `refs/*.jpg`, `fonts/`).
- `kolaj_audio.py out.wav [vo.mp3]` — muzik latar 112 BPM + SFX, campur VO (muzik merendah bila suara).
- `kolaj_timing.py` — titik sauh frasa→masa VO; seluruh suntingan diregang ikut suara.

`output/konsisten_kalahkan_viral.mp4` — episod #02 "Konsisten Kalahkan Viral" (35s, VO `assets/vo_konsisten.mp3`):
ekspresi keliru → sinis → senyum → terkejut → tunjuk, graf views melonjak lalu senyap, cop "PUTUS ASA",
loteri vs tabung syiling, kalendar ✓, ikon pelanggan bertambah, carta pertumbuhan 3 bulan, CTA "KEJAR KONSISTEN".

- `konsisten_render.py <workdir>` — guna semula enjin `kolaj_render.py`, babak disusun terus ikut masa VO (perlu `expr/9.jpg` + mask).
- `konsisten_audio.py out.wav vo.mp3` — muzik dikongsi (`kolaj_audio.make_music`) + SFX + VO.

`output/komen_idea_video.mp4` — episod #03 "Komen Pelanggan = Idea Video Percuma" (37s, VO `assets/vo_komen.mp3`).
Konsep baharu **"BALAS KOMEN"**: UI app mod gelap dengan bokeh, sticker hitam putih bergaris neon,
gelembung komen gaya TikTok yang mencurah, cop "+1 VIDEO", grid profil yang terisi, sticker "Membalas komen",
hujan hati, komen tenggelam lalu jadi content, kotak komen sedang menaip, transisi swipe-up dan glitch RGB.

- `komen_render.py <workdir>` — renderer konsep app (guna semula helper `kolaj_render.py`).
- `komen_audio.py out.wav vo.mp3` — muzik dikongsi + SFX ping/menaip/swipe + VO.
