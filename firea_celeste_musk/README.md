# Firea Celeste Musk — UGC Sales Edit (PREVIEW)

`output/preview.mp4` — 1080×1920, 30fps, 31.0s (29.9s footage + 1.1s held end card), AAC 48k, −13.5 LUFS.

## Visual direction — "Clean Soft-Pink UGC"
Tujuan: footage selfie dalam kereta rasa jujur & dekat; overlay ikut warna label Firea supaya brand konsisten.
- **Warna:** maroon `#6E1734` (teks utama / brand), rose `#D64278` (keyword, CTA), blush `#F8DCE7` (chip), krim putih (kad). Hijau/merah hanya untuk ✓/✗.
- **Font:** Poppins (ExtraBold/Bold/SemiBold) untuk keyword & sari kata; DM Serif Display Italic untuk wordmark "Firea" (dekat dengan logo label).
- **Motion:** pop dengan overshoot kecil, punch-in pada point penting, satu fokus pada satu masa. Grade jadi sejuk/pudar masa "tak selesa", kembali hangat + flash pink pada potongan produk (17.13s).
- **Audio:** pop-lofi lembut 100 BPM (F major), dijana dengan kod. Hook: pad + pluck sahaja → masalah: kick lembut → "tak selesa": muzik jadi gelap → riser masuk produk → groove penuh → tutup dengan chord + chime. Muzik di-duck ikut suara (≈17–22 dB di bawah dialog).

## Flow (dialog asal, tak dipotong / tak disusun semula)
| Masa | Dialog | Visual |
|---|---|---|
| 0–2.5 | Suka buat aktiviti dekat luar | Hook card "Suka aktiviti luar?" + slow push |
| 2.6–6.4 | tapi takut kawan tegur bau badan | Punch-in 1.2× + "BAU BADAN?" (thud) |
| 6.5–11.3 | Peluh banyak takpe, tapi jangan bau badan saja | Checklist ✓ Peluh banyak / ✗ Bau badan |
| 12.2–17.1 | …tak selesa. Orang sebelah pun tak akan mahu dekat | Grade sejuk + "TAK SELESA", muzik gelap |
| 17.13 | Firea punya power, kawal peluh, hilang terus bau badan | Whoosh + flash, kad brand + sticker botol + chip |
| 21.9–27 | So korang yang jenis kuat berpeluh tu, takut badan berbau | "Kuat berpeluh?" / "Takut badan berbau?" |
| 27.1–31 | korang pakai je Firea ni. Memang power. | End card + CTA + 0% Alkohol · 0% Paraben (dari label) |

## Edit & rebuild
- Teks, timing, CTA, zoom: `scripts/cues.py` (satu sumber timing untuk visual DAN SFX).
- Gaya/layout: `scripts/render_video.py`; muzik/SFX: `scripts/make_audio.py`; mix: `build.sh`.
- `./build.sh /path/to/python` (perlu numpy, opencv-python-headless, pillow + ffmpeg).
- `scripts/transcribe.py` — transkripsi tempatan (sherpa-onnx Whisper turbo), hanya rujukan.
- Bahan asal: `source/footage.mp4`, `source/product_photo.jpg` (salinan; fail asal tak diubah).

---

# Versi 2 — "Fresh Kinetic" (`output/preview_v2_kinetic.mp4`)
Lebih laju & bertenaga untuk wanita aktif. Dialog sama, tak dipotong.
- **Sari kata kinetik:** HURUF BESAR, 1–3 perkataan, pop + condong sedikit; keyword pink (Poppins ExtraBold, outline gelap).
- **Jump-zoom** setiap frasa (1.0–1.24×), shake pada "BAU BADAN" & "TAK SELESA" (+ glitch RGB).
- **Ikon dilukis dengan kod:** matahari (aktiviti luar), titik peluh, garis bau berombak, tanda larangan, ✓, sparkle "hapuskan" peluh & bau selepas Firea.
- **Whip-pan** merentas potongan 17.13s → botol hero di atas (muka kekal nampak) → jadi badge penjuru → end card pink + CTA kuning.
- Bar progress pink di atas.
- **Audio:** pop 118 BPM — snap → kick ringan → gelap/filter → four-on-the-floor + clap selepas produk; SFX ikut `scripts/cues_b.py`.
- Fail: `scripts/cues_b.py`, `render_video_b.py`, `make_audio_b.py`; build: `./build.sh <python> b`.

---

# Versi 3 — "Vox Explainer" (`output/preview_v3_vox.mp4`)
Gaya explainer ala Vox, ikut `vox_render.py` dalam repo ini.
- **Subjek dipotong** (rembg `u2net_human_seg`; selepas 17.13s digabung dengan `isnet-general-use` supaya botol di tangan kekal) dan diletak sebagai sticker bergaris putih di atas kertas krim + grid + grain. Kerusi/tiang kereta dibuang dengan kod (`remove_car_seat`).
- **Tipografi:** Special Elite (label mesin taip), Playfair Display Bold (tajuk + highlight marker), Anton (cop getah, callout), Permanent Marker (tulisan tangan), Inter (sari kata jalur putih + highlight kuning).
- **Diagram setiap babak:** doodle matahari → ikon kawan + belon "?!" + cop **BAU BADAN** → jadual *Peluh vs Bau badan* (Takpe ✓ / Jangan! ✗) → diagram orang menjauh → sapuan kertas → botol + callout berpanah (*Kawal peluh — Antiperspirant*, *Hilang bau badan — Odour & Wetness Protection*, dari label) → checklist *Sesuai untuk* → end card + 0% Alkohol / 0% Paraben + cop **MEMANG POWER**.
- **Framing** bertukar setiap babak (potongan keras skala/kedudukan) — tiada zoom digital pada muka.
- **Audio:** marimba 92 BPM + rim click; SFX mesin taip, kertas, cop, marker (`scripts/make_audio_vox.py`).
- Build: `./build.sh <python> vox` (perlu `rembg onnxruntime`; model dimuat turun dari GitHub release rembg ke `~/.u2net`).
