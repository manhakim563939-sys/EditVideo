# Firea Celeste Musk: Motion Ad 30s (9:16), PREVIEW

**Preview:** `output/firea_motion_ad_preview.mp4` (1080x1920, 30fps, 30.0s, AAC 48k, about -15 LUFS)
Status: **waiting for approval**. There is no final export yet.

## Flow (Awareness–Edutainment)
| Masa | Babak | Teks pada skrin |
|---|---|---|
| 0.0–3.6 | Hook | Pakai lengan panjang dari pagi *sampai malam?* · + cuaca panas & lembap |
| 3.6–7.8 | Persoalan | Pernah tak rasa ketiak cepat **PANAS & BERBAU** *walaupun dah mandi pagi?* · Jom faham puncanya |
| 7.8–12.6 | Penerangan 1 | FAKTA #1: Peluh sebenarnya hampir **TAK** berbau. Bau terhasil bila *bakteria* di kulit mengurai peluh. |
| 12.6–17.4 | Penerangan 2 | FAKTA #2: Lengan panjang = *kurang udara*. Peluh *terperangkap* lebih lama. Bakteria suka suasana **panas & lembap.** |
| 17.4–21.6 | Contoh | Satu hari *biasa*: 8:00 pagi / 1:00 tengah hari / 7:00 malam, meter "peluh terkumpul". Makin lama, makin **terasa.** |
| 21.6–25.2 | Takeaway | Berpeluh itu *normal.* Yang penting, kawal **PELUH & BAU** dari awal pagi. (foto cermin, "rutin pagi") |
| 25.2–30.0 | Produk | Logo Firea · CELESTE MUSK DEODORANT ROLL-ON · Tahan Peluh & Tahan Bau · 0% Paraben · 0% Alkohol · Khas untuk wanita bertudung yang aktif seharian. · *confidence in every touch* |

## Struktur
- `assets/src/`: salinan bahan asal (tidak diubah)
- `assets/cut/`: logo (alpha) dan crop foto, dijana oleh `prep_assets.py`
- `assets/fonts/`: Montserrat, Playfair Display Italic, Caveat (Google Fonts, OFL)
- `timeline.py`: **semua timing** (scene, cue visual, SFX) di satu tempat
- `render.py`: visual (cairo + PIL). Teks, warna dan layout setiap babak ada dalam fungsi `scene_*`
- `audio.py`: soundtrack dan SFX procedural (numpy, tiada sampel/muzik komersial)

## Render semula
```bash
python3 -m venv .venv && .venv/bin/pip install pycairo numpy pillow
.venv/bin/python prep_assets.py
.venv/bin/python audio.py          # build/audio.wav
.venv/bin/python render.py         # build/video.mp4 (about 1 minute)
ffmpeg -y -i build/video.mp4 -i build/audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output/firea_motion_ad_preview.mp4
.venv/bin/python render.py --still 9.5 20   # semak frame tertentu -> build/still_*.png
```
