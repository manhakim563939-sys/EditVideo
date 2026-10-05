import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import T from './timeline.json';
import {C, FONT} from './theme';
import {COPY} from './copy';
import {morphState, shapePoints, toPath} from './shapes';

type CueKey = keyof typeof T.cues;
type SceneKey = keyof typeof T.scenes;
const S = T.scenes;
const q = (k: CueKey) => T.cues[k];
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// teks & foto keluar sebelum morph bermula (morph = babak tamat - 8)
const outOf = (s: SceneKey) => S[s].to - 12;

const useAppear = (at: number, out: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - at, fps, config: {damping: 18, mass: 0.6, stiffness: 140}});
  const o = interpolate(f, [out, out + 6], [1, 0], clamp);
  return {p, o, on: f >= at && f < out + 6};
};

// Teks: bergerak bebas daripada morph — naik lembut, kemudian diam.
type LineProps = {at: number; out: number; y: number; size: number; color?: string; weight?: number; x?: number; w?: number; children: React.ReactNode};
const Line: React.FC<LineProps> = ({at, out, y, size, color = C.text, weight = 800, x = 0, w = 1080, children}) => {
  const {p, o, on} = useAppear(at, out);
  if (!on) return null;
  return (
    <div
      style={{
        position: 'absolute', left: x, width: w, top: y, textAlign: 'center',
        fontFamily: FONT, fontWeight: weight, fontSize: size, lineHeight: 1.05, letterSpacing: '-0.015em',
        color, opacity: Math.min(1, p * 1.4) * o, transform: `translateY(${(1 - p) * 46}px)`, whiteSpace: 'nowrap',
      }}
    >
      {children}
    </div>
  );
};

const Shapes: React.FC = () => {
  const f = useCurrentFrame();
  const fill = [C.accent, C.text, C.accent];
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      {[0, 1, 2].map((i) => (
        <path key={i} d={toPath(shapePoints(i, f))} fill={fill[i]} />
      ))}
    </svg>
  );
};

type Place = {src: string; sw: number; fx: number; fy: number; s: number; cx: number; cy: number};
// Foto dalam bingkai B (krim) — topeng ikut bentuk B ditolak 16px, imej tidak diherot.
// place2 + seg: foto bergerak ke kedudukan baharu bersama morph segmen `seg` (babak seg -> seg+1).
const Photo: React.FC<{at: number; out: number; place: Place; place2?: Place; seg?: number}> = ({at, out, place, place2, seg = -1}) => {
  const f = useCurrentFrame();
  const {p, o, on} = useAppear(at, out);
  if (!on) return null;
  const m = morphState(f);
  const t = !place2 ? 0 : m.from > seg ? 1 : m.from === seg ? m.t : 0;
  const L = (a: number, b: number) => a + (b - a) * t;
  const P = place2 ?? place;
  const s = L(place.s, P.s);
  const cx = L(place.cx, P.cx);
  const cy = L(place.cy, P.cy);
  const clip = toPath(shapePoints(1, f, 16));
  return (
    <AbsoluteFill style={{clipPath: `path('${clip}')`, opacity: Math.min(1, p * 1.5) * o}}>
      <Img
        src={staticFile(place.src)}
        style={{
          position: 'absolute', width: place.sw * s, maxWidth: 'none',
          left: cx - place.fx * s, top: cy - place.fy * s,
          transform: `scale(${1.08 - 0.08 * p})`, transformOrigin: `${cx}px ${cy}px`,
        }}
      />
    </AbsoluteFill>
  );
};

const ZeroBadge: React.FC<{at: number; cx: number; label: string}> = ({at, cx, label}) => {
  const out = outOf('zero');
  return (
    <>
      <Line at={at} out={out} y={680} size={170} color={C.bg} x={cx - 220} w={440}>
        0%
      </Line>
      <Line at={at + 6} out={out} y={1010} size={64} x={cx - 220} w={440}>
        {label}
      </Line>
    </>
  );
};

export const FireaLiquid: React.FC = () => {
  const o = (s: SceneKey) => outOf(s);
  return (
    <AbsoluteFill style={{background: C.bg}}>
      {/* seluruh komposisi diturunkan 60px untuk imbangan ruang negatif dalam 9:16 */}
      <AbsoluteFill style={{transform: 'translateY(60px)'}}>
      <Shapes />

      {/* 1. HOOK */}
      <Photo at={q('hook_photo')} out={o('hook')} place={{src: 'img/1.jpg', sw: 720, fx: 370, fy: 600, s: 1.15, cx: 500, cy: 640}} />
      <Line at={q('hook_t1')} out={o('hook')} y={1180} size={100}>{COPY.hook[0]}</Line>
      <Line at={q('hook_t2')} out={o('hook')} y={1300} size={84}>{COPY.hook[1]}</Line>
      <Line at={q('hook_t3')} out={o('hook')} y={1410} size={100} color={C.accent}>{COPY.hook[2]}</Line>

      {/* 2. MASALAH */}
      <Line at={q('prob_t1')} out={o('prob')} y={1180} size={104}>{COPY.prob[0]}</Line>
      <Line at={q('prob_t2')} out={o('prob')} y={1310} size={136} color={C.accent}>{COPY.prob[1]}</Line>
      <Line at={q('prob_t3')} out={o('prob')} y={1490} size={46} weight={500}>{COPY.prob[2]}</Line>

      {/* 3–4. PRODUK + USP (foto sama, bingkai mengecil) */}
      <Photo
        at={q('story_photo')}
        out={o('usp')}
        seg={2}
        place={{src: 'img/3.jpg', sw: 1125, fx: 512, fy: 990, s: 0.8, cx: 540, cy: 640}}
        place2={{src: 'img/3.jpg', sw: 1125, fx: 512, fy: 990, s: 0.66, cx: 540, cy: 540}}
      />
      <Line at={q('story_t1')} out={o('story')} y={1270} size={88}>{COPY.story[0]}</Line>
      <Line at={q('story_t2')} out={o('story')} y={1390} size={64} color={C.accent}>{COPY.story[1]}</Line>
      <Line at={q('story_t3')} out={o('story')} y={1480} size={38} weight={500}>{COPY.story[2]}</Line>

      <Line at={q('usp_t1')} out={o('usp')} y={1080} size={110} color={C.accent}>{COPY.usp[0]}</Line>
      <Line at={q('usp_t2')} out={o('usp')} y={1205} size={110}>{COPY.usp[1]}</Line>
      <Line at={q('usp_t3')} out={o('usp')} y={1380} size={46} weight={500}>{COPY.usp[2]}</Line>
      <Line at={q('usp_t4')} out={o('usp')} y={1445} size={46} weight={500}>{COPY.usp[3]}</Line>

      {/* 5. 0% */}
      <ZeroBadge at={q('zero_n1')} cx={300} label={COPY.zero.a} />
      <ZeroBadge at={q('zero_n2')} cx={780} label={COPY.zero.b} />
      <Line at={q('zero_t')} out={o('zero')} y={1190} size={54} weight={500}>{COPY.zero.note[0]}</Line>
      <Line at={q('zero_t') + 6} out={o('zero')} y={1260} size={54} weight={500}>{COPY.zero.note[1]}</Line>

      {/* 6. GAYA HIDUP */}
      <Photo at={q('life_photo')} out={o('life')} place={{src: 'img/2.jpg', sw: 768, fx: 420, fy: 520, s: 1.0, cx: 540, cy: 640}} />
      <Line at={q('life_t1')} out={o('life')} y={1210} size={120} color={C.accent}>{COPY.life[0]}</Line>
      <Line at={q('life_t2')} out={o('life')} y={1345} size={84}>{COPY.life[1]}</Line>

      {/* 7. CTA (tiada keluar) */}
      <Photo at={q('cta_photo')} out={9999} place={{src: 'img/5.jpg', sw: 768, fx: 380, fy: 470, s: 1.14, cx: 540, cy: 560}} />
      <Line at={q('cta_name')} out={9999} y={1030} size={76}>{COPY.cta.name}</Line>
      <CtaButton />
      <Line at={q('cta_tag')} out={9999} y={1320} size={40} weight={500}>{COPY.cta.tag}</Line>

      </AbsoluteFill>
      <Audio src={staticFile('audio/soundtrack.wav')} />
    </AbsoluteFill>
  );
};

const CtaButton: React.FC = () => {
  const f = useCurrentFrame();
  const {p, on} = useAppear(q('cta_btn'), 9999);
  if (!on) return null;
  const breathe = 1 + Math.sin((f - q('cta_btn')) / 6) * 0.015;
  return (
    <div style={{position: 'absolute', top: 1140, width: 1080, display: 'flex', justifyContent: 'center'}}>
      <div
        style={{
          background: C.accent, borderRadius: 999, padding: '28px 64px',
          fontFamily: FONT, fontWeight: 800, fontSize: 56, color: C.bg, letterSpacing: '0.02em',
          transform: `scale(${(0.7 + 0.3 * p) * breathe})`, opacity: Math.min(1, p * 2),
        }}
      >
        {COPY.cta.button}
      </div>
    </div>
  );
};
