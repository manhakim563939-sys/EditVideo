# Aimi Curtain — Kinetic Typography (PREVIEW)

`output/preview_aimi_curtain.mp4` — 1080×1920, 30fps, 47.5s (44.9s dialog asal + 2.6s end card).
**Status: PREVIEW — tunggu approval sebelum final export.**

## Struktur
```
src/timeline.py   semua cue masa, teks, warna (edit di sini dahulu)
src/render.py     visual: punch-in, cutaway + wipe, kinetic text, testimoni, end card
src/audio.py      muzik instrumental + SFX procedural (dari cue yang sama)
render.sh         jana audio -> render video -> mix (ducking + limiter) -> output/
assets/fonts/     Montserrat 900 + Inter 500 (SIL OFL, dari @fontsource)
assets/source/    BAHAN ASAL (tidak di-commit) — letak fail ini:
                  talking_head.mp4  (VID-20260925-WA0007.mp4)
                  broll_curtain.mp4 (VID-20260929-WA0029.mp4)
                  testimoni_1.jpg, testimoni_2.jpg, foto_langsir.jpg
```
Jalankan: `./render.sh` (perlu ffmpeg + python3; venv `.venv` dicipta automatik).
`MIX_ONLY=1 ./render.sh` = jana semula audio/mix sahaja tanpa render visual.

## Garis masa
| Masa | Visual | Teks |
|---|---|---|
| 0.0–2.8 | Talking head, slow push-in | RUMAH BARU? |
| 2.8–5.5 | Jump cut, punch-in | NAK CERIAKAN / SUASANA? |
| 5.6–8.0 | | [AIMI CURTAIN] LANGSIR / TEMPAHAN |
| 8.0–11.8 | Tiada teks (ruang bernafas) | — |
| 11.9–15.7 | Wide shot | DARI KONSULTASI / sampai / SIAP PASANG (USP) |
| 16.1–20.4 | Cutaway B-roll langsir (wipe emas) | [HASIL KERJA AIMI CURTAIN] |
| 20.5–24.5 | Testimoni 1, highlight “Kain cantik dan tebal..” | [MAKLUM BALAS PELANGGAN] |
| 24.6–27.6 | Cutaway foto langsir (pan, berakhir pada logo) | HASIL / SIAP PASANG |
| 27.7–31.3 | Testimoni 2, highlight “harga pun murah n berpatutan” | |
| 34.3–37.8 | Showroom kain | BANYAK PILIHAN / WARNA KAIN |
| 42.8–44.9 | | NAK LANGSIR / SIAP PASANG? |
| 44.9–47.5 | End card logo | AIMI CURTAIN / Hubungi kami untuk konsultasi langsir (CTA SEMENTARA) |

Dialog asal dikekalkan 100%: tiada potongan, tiada susun semula, tiada speed-up.
Audio: dialog dinormalkan ke −16 LUFS; muzik ~19 dB di bawah dialog (side-chain duck); SFX click/whoosh/pop/riser/impact ikut cue.
