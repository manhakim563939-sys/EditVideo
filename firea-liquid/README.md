# Firea Celeste Musk — Liquid Shape Flow (PREVIEW)

9:16 · 1080×1920 · 30fps · 30s · 100% motion ad. Ini **preview**, bukan final export.

- Preview: `out/firea-liquid-preview.mp4`
- Teks: `src/copy.ts` · Timing + cue SFX: `src/timeline.json`
- Bentuk cecair & keyframe morph: `src/shapes.ts` · Komposisi: `src/FireaLiquid.tsx` · Warna/font: `src/theme.ts`
- Audio procedural: `scripts/make-audio.mjs` → `public/audio/soundtrack.wav` (sweep morph guna formula sama dengan shapes.ts)
- Aset: `public/img/1–5.jpg` (salinan bahan asal); font Outfit (OFL)

```
npm install
npm run preview   # jana audio + render
npm run studio    # edit visual
```
Buang flag `--browser-executable` dalam package.json jika render di komputer sendiri.

## Flow (morph menyambung makna)
0–4s Hook: blob + bingkai bulat foto 1 → 4–9s blob jadi **titisan peluh** (Ketiak berpeluh? Risau bau?) →
9–14s titisan mendarat jadi bingkai produk (foto 3) → 14–19s bingkai mengecil, Tahan peluh / Tahan bau →
19–23.5s pecah jadi **dua bulatan 0%** (Alkohol / Paraben) → 23.5–27s bergabung semula, 50ml dalam beg (foto 2) →
27–30s CTA (foto 5) — **CTA SEMENTARA: "DAPATKAN SEKARANG"**
