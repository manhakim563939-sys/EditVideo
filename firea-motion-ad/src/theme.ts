import {continueRender, delayRender, staticFile} from 'remotion';

// Montserrat (OFL) disimpan setempat dalam public/fonts — satu keluarga sahaja:
// 900 untuk headline, 500 untuk teks sokongan.
export const FONT = 'Montserrat';

if (typeof document !== 'undefined') {
  const handle = delayRender('Memuatkan font Montserrat');
  const faces = [
    new FontFace(FONT, `url(${staticFile('fonts/Montserrat-wght.woff2')}) format('woff2')`, {weight: '100 900', style: 'normal'}),
    new FontFace(FONT, `url(${staticFile('fonts/Montserrat-Italic-wght.woff2')}) format('woff2')`, {weight: '100 900', style: 'italic'}),
  ];
  Promise.all(faces.map((f) => f.load()))
    .then((loaded) => {
      loaded.forEach((f) => document.fonts.add(f));
      continueRender(handle);
    })
    .catch((err) => {
      throw err;
    });
}

// Peranan warna daripada brief (bg gelap / teks putih / satu aksen),
// diadaptasi kepada palet jenama Firea (merah jambu + maroon pada label).
export const C = {
  bg: '#1B1219',
  bg2: '#2A1622',
  text: '#FFFFFF',
  sub: '#E9D9E1',
  accent: '#F7A6C8',
  maroon: '#8E1F45',
};
