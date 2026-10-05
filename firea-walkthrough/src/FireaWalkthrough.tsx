import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import T from './timeline.json';
import {C, FONT} from './theme';
import {CAPTIONS, CTA, STEPS} from './copy';
import {camera, shotAt} from './camera';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const CARD_BOTTOM = 260; // kad kapsyen berakhir pada y=1660 (jauh dari kawalan platform)
const CTA_FROM = T.shots[T.shots.length - 1].from;

const useIn = (at: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - at, fps, config: {damping: 20, mass: 0.6, stiffness: 150}});
};

// ---------------------------------------------------------------- viewport
const Viewport: React.FC = () => {
  const f = useCurrentFrame();
  const shot = shotAt(f);
  const {left, top, z} = camera(shot, f);
  // potongan skala terus pada permulaan shot (punch yang disengajakan, bukan goyang)
  const punch = interpolate(f - shot.from, [0, 8], [1.05, 1], clamp);
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${punch})`}}>
        <Img
          src={staticFile(shot.src)}
          style={{position: 'absolute', maxWidth: 'none', width: shot.sw * z, left: -left * z, top: -top * z}}
        />
        {T.boxes
          .filter((b) => f >= b.from && f < b.to + 6 && b.from >= shot.from && b.from < shot.to)
          .map((b) => (
            <FocusBox key={b.from} b={b} left={left} top={top} z={z} />
          ))}
      </div>
    </AbsoluteFill>
  );
};

// Kotak fokus: menandakan kawasan yang sedang dibaca (bukan klik). Luar kotak dimalapkan sedikit.
const FocusBox: React.FC<{b: (typeof T.boxes)[number]; left: number; top: number; z: number}> = ({b, left, top, z}) => {
  const f = useCurrentFrame();
  const p = useIn(b.from);
  const o = interpolate(f, [b.to, b.to + 6], [1, 0], clamp) * Math.min(1, p * 1.5);
  const pad = 14;
  return (
    <div
      style={{
        position: 'absolute',
        left: (b.x - left) * z - pad,
        top: (b.y - top) * z - pad,
        width: b.w * z + pad * 2,
        height: b.h * z + pad * 2,
        border: '6px solid #fff',
        borderRadius: 22,
        boxShadow: `0 0 0 3px ${C.maroon}, 0 0 0 3000px rgba(20,8,14,${0.32 * o})`,
        opacity: o,
        transform: `scale(${1.12 - 0.12 * p})`,
      }}
    />
  );
};

// ---------------------------------------------------------------- langkah
const StepChip: React.FC = () => {
  const f = useCurrentFrame();
  const steps = T.steps;
  const cur = steps.findIndex((s) => f >= s.from && f < s.to);
  const last = steps[steps.length - 1];
  const vis = interpolate(f, [steps[0].from, steps[0].from + 10, last.to - 6, last.to], [0, 1, 1, 0], clamp);
  const idx = cur < 0 ? (f < steps[0].from ? 0 : steps.length - 1) : cur;
  const s = steps[idx];
  const swap = useIn(s.from);
  if (vis <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 70, top: 150, width: 940, opacity: vis}}>
      <div
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 18, background: C.maroon, borderRadius: 999,
          padding: '14px 30px', boxShadow: '0 8px 20px rgba(0,0,0,0.3)',
        }}
      >
        <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 34, color: C.pink}}>
          LANGKAH {idx + 1}/{steps.length}
        </span>
        <span
          style={{
            fontFamily: FONT, fontWeight: 700, fontSize: 34, color: '#fff',
            opacity: swap, transform: `translateX(${(1 - swap) * 16}px)`, display: 'inline-block',
          }}
        >
          {STEPS[s.id]}
        </span>
      </div>
      <div style={{display: 'flex', gap: 10, marginTop: 16}}>
        {steps.map((st, i) => {
          const fill = interpolate(f, [st.from, st.to], [0, 1], clamp);
          return (
            <div key={st.id} style={{flex: 1, height: 8, borderRadius: 8, background: 'rgba(255,255,255,0.45)', overflow: 'hidden'}}>
              <div style={{width: `${fill * 100}%`, height: '100%', background: C.pink}} />
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- kapsyen
const CaptionCard: React.FC = () => {
  const f = useCurrentFrame();
  if (f >= CTA_FROM) return null;
  const cardIn = interpolate(f, [0, 8, CTA_FROM - 6, CTA_FROM], [0, 1, 1, 0], clamp);
  const cap = T.captions.find((c) => f >= c.from && f < c.to);
  return (
    <div
      style={{
        position: 'absolute', left: 70, right: 70, bottom: CARD_BOTTOM, height: 250,
        background: C.card, borderRadius: 30, boxShadow: '0 14px 34px rgba(0,0,0,0.35)',
        padding: '0 44px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
        opacity: cardIn, transform: `translateY(${(1 - cardIn) * 40}px)`,
      }}
    >
      {cap && <CaptionText key={cap.id} id={cap.id} from={cap.from} to={cap.to} />}
    </div>
  );
};

const CaptionText: React.FC<{id: string; from: number; to: number}> = ({id, from, to}) => {
  const f = useCurrentFrame();
  const p = useIn(from);
  const o = interpolate(f, [to - 5, to], [1, 0], clamp);
  const c = CAPTIONS[id];
  return (
    <div style={{opacity: Math.min(1, p * 1.4) * o, transform: `translateY(${(1 - p) * 18}px)`}}>
      {c.kicker && (
        <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 32, color: C.maroon, marginBottom: 10}}>{c.kicker}</div>
      )}
      <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 58, lineHeight: 1.12, color: C.ink, letterSpacing: '-0.01em', whiteSpace: 'pre-line'}}>
        {c.main}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- CTA
const CtaCard: React.FC = () => {
  const f = useCurrentFrame();
  const a = useIn(CTA_FROM);
  const n = useIn(T.cta.name);
  const b = useIn(T.cta.btn);
  const t = useIn(T.cta.tag);
  if (f < CTA_FROM) return null;
  const fade = (p: number) => ({opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 18}px)`});
  return (
    <div
      style={{
        position: 'absolute', left: 70, right: 70, bottom: CARD_BOTTOM, height: 340,
        background: C.card, borderRadius: 30, boxShadow: '0 14px 34px rgba(0,0,0,0.35)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 22,
        opacity: a, transform: `translateY(${(1 - a) * 40}px)`,
      }}
    >
      <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 62, color: C.ink, ...fade(n)}}>{CTA.name}</div>
      <div
        style={{
          fontFamily: FONT, fontWeight: 800, fontSize: 46, color: '#fff', background: C.maroon,
          borderRadius: 999, padding: '20px 54px', letterSpacing: '0.02em', ...fade(b),
        }}
      >
        {CTA.button}
      </div>
      <div style={{fontFamily: FONT, fontWeight: 500, fontStyle: 'italic', fontSize: 32, color: C.maroon, ...fade(t)}}>{CTA.tag}</div>
    </div>
  );
};

export const FireaWalkthrough: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <Viewport />
    {/* kecerunan nipis atas supaya cip langkah sentiasa terbaca */}
    <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 18%)'}} />
    <StepChip />
    <CaptionCard />
    <CtaCard />
    <Audio src={staticFile('audio/soundtrack.wav')} />
  </AbsoluteFill>
);
