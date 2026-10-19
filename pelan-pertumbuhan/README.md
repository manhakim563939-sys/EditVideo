# Pelan Pertumbuhan Aimi Curtain — Motion Graphics

`preview_v1.mp4` — preview 1920×1080 (16:9), 30fps, ~3:31. Text-led (belum ada VO), dengan muzik & SFX procedural. **Belum final export.**

`SKRIP_VO.md` — skrip VO untuk ElevenLabs, ikut babak (s01–s19) + teks penuh.

## Struktur
- `script/scenes.json` — SUMBER UTAMA: skrip VO setiap babak, perkataan cue, dan teks pada skrin.
- `audio/build.py` — kira timeline (`src/timeline.json`) daripada skrip/VO, jana `public/music.wav` & `public/sfx.wav`.
- `src/Scenes.tsx` — susun atur babak (pembuka, peta fasa, tajuk fasa, tindakan, matlamat/KPI, penutup).
- `src/Viz.tsx` — infografik animasi setiap tindakan.
- `src/theme.ts` — warna emerald/emas & font (Lora + Poppins) ikut slaid.
- `public/img/` — logo (dipotong dari slaid) & foto kerja pemasangan sebenar.

## Masukkan VO ElevenLabs
1. Simpan fail sebagai `public/vo/s01.mp3` … `public/vo/s19.mp3`.
2. `.venv/bin/python audio/build.py` (sekali `python3 -m venv .venv && .venv/bin/pip install numpy scipy soundfile` jika belum ada).
3. `npx remotion render src/index.ts Main out/video.mp4 --crf=18`

Babak akan memanjang/memendek ikut VO sebenar; muzik di-duck di bawah suara secara automatik.

## VO semasa
- `vo-source/elevenlabs_aina_full.mp3` — fail asal ElevenLabs (suara "Aina").
- `vo-source/segments.json` — titik potong setiap babak (dijumpai dengan padanan jeda + transkripsi Whisper).
- `vo-source/cue_times.json` — masa sebenar perkataan cue dalam setiap fail VO; `build.py` guna ini supaya animasi tepat pada suara.
- `public/vo/s01.wav … s19.wav` — VO yang telah dinormalkan (−16 LUFS) dan dipotong ikut babak.
