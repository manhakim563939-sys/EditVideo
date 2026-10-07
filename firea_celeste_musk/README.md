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
