# Firea Celeste Musk: "MITOS atau FAKTA?" (30s, 9:16), PREVIEW

**Preview:** `output/firea_mitos_fakta_preview.mp4` (1080x1920, 30fps, 30.0s, AAC, about -17 LUFS)
Status: **waiting for approval**. There is no final export yet.

Konsep: kuiz game-show interaktif. Penonton teka dulu (timer berdetik), kemudian cop MITOS!/FAKTA! dihentak atas kad, diikuti penerangan ringkas. Penutup ialah product reveal dengan sticker USP.

| Masa | Babak | Isi |
|---|---|---|
| 0–3 | Hook | Foto penuh (gambar 9, angkat tangan + produk) · **MITOS** *atau* **FAKTA?** · "Edisi ketiak berpeluh" · "3 soalan. Teka dulu…" |
| 3–10 | Soalan 1 | "Bau ketiak datang dari peluh." → **MITOS** · Peluh hampir TAK berbau; bau terhasil bila bakteria di kulit mengurai peluh. |
| 10–17 | Soalan 2 | "Lengan panjang lindungi ketiak dari bau." → **MITOS** · Kain menutup = kurang udara; peluh terperangkap, bakteria suka panas & lembap. |
| 17–23 | Soalan 3 | "Berpeluh itu normal." → **FAKTA** · Badan berpeluh untuk sejukkan diri. Yang penting, kawal PELUH & BAU. |
| 23–30 | Reveal | "Ketiak berpeluh? *Dah tak risau lagi.*" · botol (cutout gambar 6) · sticker: Tahan Peluh & Bau / Cepat Kering / 0% Alkohol / 0% Paraben · logo · "Hidup aktif, keyakinan bermula di sini!" · "Berapa soalan awak teka betul? Komen!" |

## Bahan yang digunakan
- **9.jpg**: hook (full-bleed)
- **6.jpg**: botol (cutout; cap dilukis semula kerana tajuk poster bertindih di atasnya)
- **5.jpg**: polaroid soalan 1
- **7.jpg**: polaroid soalan 2
- **8.jpg**: polaroid soalan 3
- **1.jpg**: logo
- **10.jpg** sama dengan 5.jpg, jadi tidak digunakan.

Copy jenama diambil daripada poster: "Ketiak berpeluh, dah tak risau lagi", "Hidup aktif, keyakinan bermula di sini!", "Cepat kering", "0% Alkohol / 0% Paraben", "Tahan peluh & bau".

## Struktur
- `timeline.py`: semua timing + teks kuiz (ubah soalan/jawapan di sini)
- `render.py`: visual
- `fx.py`: toolkit lukisan
- `audio.py` / `synth.py`: muzik + SFX procedural
- `prep_assets.py`: logo, cutout botol, crop foto

## Render semula
```bash
python3 -m venv .venv && .venv/bin/pip install pycairo numpy pillow scipy
.venv/bin/python prep_assets.py && .venv/bin/python audio.py && .venv/bin/python render.py
ffmpeg -y -i build/video.mp4 -i build/audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output/firea_mitos_fakta_preview.mp4
```
