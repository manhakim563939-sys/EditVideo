import {continueRender, delayRender, staticFile} from 'remotion';

export const FONT = 'Outfit';

if (typeof document !== 'undefined') {
  const handle = delayRender('Memuatkan font Outfit');
  new FontFace(FONT, `url(${staticFile('fonts/Outfit.woff2')}) format('woff2')`, {weight: '100 900'})
    .load()
    .then((f) => {
      document.fonts.add(f);
      continueRender(handle);
    });
}

// Palet tiga warna (peranan daripada brief: latar / teks / aksen), diadaptasi ke jenama Firea:
// ungu brief -> maroon logo Firea, emas brief -> merah jambu label. Krim kekal untuk teks.
export const C = {
  bg: '#4A1530',
  text: '#FFF3E0',
  accent: '#F4A6C6',
};
