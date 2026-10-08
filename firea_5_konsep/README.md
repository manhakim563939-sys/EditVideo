# Firea Celeste Musk: 5 konsep video (30s, 9:16), PREVIEW

Semua preview masih **menunggu approval**. Belum ada final export.

| # | Folder | Konsep | Masalah audience |
|---|---|---|---|
| 1 | `v1_angkat_tangan/` | **Momen Angkat Tangan**: 4 momen harian (LRT, meeting, rak atas, peluk kawan) dengan bisikan hati → "Kenapa kita kena risau benda yang normal?" → produk → foto sebenar (gambar 9) "Angkat tangan tanpa risau." | Takut orang perasan bila angkat tangan |
| 2 | `v2_jam_risau/` | **Jam Berapa Awak Mula Risau?**: jam 7 pagi → 9 malam dengan meter "TAHAP YAKIN" yang menurun → REWIND → ulang hari dengan Firea → end card | Keyakinan menurun sepanjang hari aktif |
| 3 | `v3_lengan_panjang/` | **Dilema Lengan Panjang**: split screen *Nasihat Internet* vs *Realiti Kita* → "Kita tak boleh ubah cara berpakaian, tapi boleh pilih perlindungan yang betul" → produk → ayat jenama "Khas untuk wanita bertudung…" | Nasihat umum tak sesuai untuk wanita bertutup |
| 4 | `v4_red_flag/` | **3 Red Flag Deodorant**: Melekit / Lambat kering / Ada alkohol → setiap satu dijawab "green flag" dari label Firea → recap → ajakan komen | Pengalaman tak selesa dengan deodorant |
| 5 | `v5_dear_ketiak/` | **Dear Ketiak**: surat tulisan tangan di kertas buku → tone bertukar "Tapi hari ni, aku dah ada geng baru" → P.S. fakta produk → polaroid gambar 9 → sign-off | Rasa malu yang jarang dicakap |

Setiap folder: `video.py` (timing, teks, babak, cue SFX, muzik) dan `output/<nama>_preview.mp4`.
Toolkit dikongsi dalam `common/`:
- `fx.py`: lukisan, watak ilustrasi, transisi
- `music.py`: muzik dan SFX procedural
- `build.py`: render, mux, ukur loudness
- `prep_assets.py`: aset
- `assets/`: bahan asal dan crop

## Fakta yang digunakan (semua daripada bahan yang diberi)
- **Tahan peluh & bau / perlindungan bau & peluh sepanjang hari:** brief, poster 3, poster 8
- **Bantu kawal peluh & lindungi daripada bau ketiak:** brief audience, gambar 7
- **Cepat kering (Quick dry), tak melekit (Non sticky):** label botol, poster 8
- **0% Alkohol, 0% Paraben:** brief, label, poster
- **Slogan:** "confidence in every touch", "Ketiak berpeluh, dah tak risau lagi", "Hidup aktif, keyakinan bermula di sini!", "Khas untuk wanita bertudung yang aktif seharian, walaupun sentiasa berlengan panjang."

## Render semula
```bash
python3 -m venv .venv && .venv/bin/pip install pycairo numpy pillow scipy
(cd common && ../.venv/bin/python prep_assets.py)
.venv/bin/python common/build.py v1_angkat_tangan            # -> v1_angkat_tangan/output/...
.venv/bin/python common/build.py v1_angkat_tangan --still 5 12  # frame semakan
```
