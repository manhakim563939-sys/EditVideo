import {continueRender, delayRender, staticFile} from 'remotion';

export const FONT = 'Montserrat';

if (typeof document !== 'undefined') {
  const handle = delayRender('Memuatkan font');
  new FontFace(FONT, `url(${staticFile('fonts/Montserrat-wght.woff2')}) format('woff2')`, {weight: '100 900'})
    .load()
    .then((f) => {
      document.fonts.add(f);
      continueRender(handle);
    });
}

// Jenama Firea (daripada label): maroon + merah jambu. Kad kapsyen putih untuk kontras.
export const C = {
  ink: '#2A1622',
  maroon: '#8E1F45',
  pink: '#F7A6C8',
  card: '#FFFFFF',
};
