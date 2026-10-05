import {continueRender, delayRender, staticFile} from 'remotion';

// Dua keluarga sahaja: Archivo (headline editorial + teks sokongan), Permanent Marker (anotasi).
export const SANS = 'Archivo';
export const MARKER = 'Permanent Marker';

if (typeof document !== 'undefined') {
  const handle = delayRender('Memuatkan font');
  const faces = [
    new FontFace(SANS, `url(${staticFile('fonts/Archivo.woff2')}) format('woff2')`, {weight: '100 900'}),
    new FontFace(MARKER, `url(${staticFile('fonts/PermanentMarker.woff2')}) format('woff2')`),
  ];
  Promise.all(faces.map((f) => f.load())).then((loaded) => {
    loaded.forEach((f) => document.fonts.add(f));
    continueRender(handle);
  });
}

// Peranan warna brief (kertas / dakwat / aksen) diadaptasi kepada jenama Firea:
// aksen oren brief ditukar kepada maroon logo Firea; merah jambu label untuk pita & highlight.
export const C = {
  paper: '#E9DFC9',
  card: '#FBF8F1',
  ink: '#22211F',
  accent: '#8E1F45',
  tape: 'rgba(242, 166, 198, 0.78)',
  highlight: 'rgba(247, 166, 200, 0.55)',
};
