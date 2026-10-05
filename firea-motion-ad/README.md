# Firea Celeste Musk — Motion Ad (PREVIEW)

9:16 · 1080×1920 · 30fps · 30s · 100% motion ad, gaya Kinetic Typography.
Ini **preview**, bukan final export. Final export hanya selepas diluluskan.

- Preview: `out/firea-preview.mp4`
- Teks atas skrin: `src/copy.ts` (edit di sini sahaja)
- Timing babak + cue SFX (dikongsi visual & audio): `src/timeline.json`
- Babak/animasi: `src/FireaAd.tsx`, `src/kit.tsx`; warna & font: `src/theme.ts`
- Soundtrack/SFX procedural: `scripts/make-audio.mjs` → `public/audio/soundtrack.wav`
- Aset: `public/img/1–5.jpg` (salinan bahan asal), font Montserrat (OFL) dalam `public/fonts`

## Render semula
```
npm install
npm run preview        # jana audio + render out/firea-preview.mp4
npm run studio         # edit secara visual (Remotion Studio)
```
`--browser-executable` dalam package.json menunjuk ke Chromium dalam sesi cloud ini;
buang flag itu jika render di komputer sendiri.

## Flow (saat)
0–3.5 Hook: Bertudung / berlengan panjang / aktif seharian (foto 1)
3.5–9.5 Masalah: Ketiak berpeluh? Risau bau?
9.5–13.5 Pusingan: "Dah tak risau lagi" → reveal produk (foto 3) + nama
13.5–19.5 USP: Tahan peluh · Tahan bau · Cepat kering, tak melekit · Kesegaran tahan lama
19.5–23.5 0% Alkohol · 0% Paraben · formula lembut, guna harian
23.5–26.5 50ml muat dalam beg (foto 2)
26.5–30 CTA (foto 5) — **CTA SEMENTARA: "DAPATKAN SEKARANG"**
