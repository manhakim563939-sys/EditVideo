# EditVideo

`output/vox_style_edit.mp4` — klip asal (VID-20260928-WA0017) dengan background dibuang dan diedit semula gaya Vox:
latar kertas bertekstur + grid, subjek sebagai potongan "sticker" bergaris putih, kad tajuk animasi,
diagram (ikon orang, carta duit menurun, garis masa 2 tahun, kiraan RM), cop "TETAP PEMBAZIRAN", dan sari kata.

`vox_render.py` — skrip render (perlukan frame 30fps + mask `rembg u2net_human_seg` + font Google).

## HyperFrames (edit video guna HTML + GSAP)

[HyperFrames](https://hyperframes.heygen.com) dipasang sebagai dev dependency. Projek komposisi ada dalam `hyperframes/` (portrait 1080x1920).

```bash
npm install              # pasang hyperframes + gsap
npm run hf:browser       # muat turun Chrome headless untuk render (sekali sahaja)
npm run hf:dev           # buka studio preview
npm run hf:check         # lint + semakan runtime/layout
npm run hf:render        # render ke MP4
```

- Edit `hyperframes/index.html` — setiap elemen guna `data-start` / `data-duration` / `data-track-index`, animasi guna GSAP timeline (`window.__timelines["main"]`).
- GSAP disimpan dalam `hyperframes/vendor/gsap.min.js` supaya render jalan tanpa CDN.
- Panduan untuk AI: `hyperframes/CLAUDE.md`.
