import {continueRender, delayRender, staticFile} from 'remotion';

export const BODY = 'Montserrat';
export const PIXEL = 'VT323';

if (typeof document !== 'undefined') {
  const handle = delayRender('Memuatkan font');
  Promise.all([
    new FontFace(BODY, `url(${staticFile('fonts/Montserrat-wght.woff2')}) format('woff2')`, {weight: '100 900'}).load(),
    new FontFace(PIXEL, `url(${staticFile('fonts/VT323.woff2')}) format('woff2')`).load(),
  ]).then((fs) => {
    fs.forEach((f) => document.fonts.add(f));
    continueRender(handle);
  });
}

// Peranan brief: desktop (#93aaa8) / teks (#172b31) / aksen krim (#e6dfbd),
// diadaptasi ke jenama Firea: desktop merah jambu pudar, bar tajuk maroon logo, muka tetingkap krim.
export const C = {
  desk: '#C9A2B3',
  deskDot: '#BB92A4',
  ink: '#2A1622',
  face: '#F3EADB',
  title: '#8E1F45',
  pink: '#F7A6C8',
  light: '#FFFFFF',
  shadow: '#7C5A69',
};
