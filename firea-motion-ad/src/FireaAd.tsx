import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timeline.json';
import {C, FONT} from './theme';
import {COPY} from './copy';
import {Check, FadeIn, H, MaskUp, Photo, Punch, Sub, clamp, useExit, useSpring} from './kit';

type CueKey = keyof typeof T.cues;
const S = T.scenes;
// cue global -> frame tempatan babak
const at = (scene: keyof typeof S, k: CueKey) => T.cues[k] - S[scene].from;
const dur = (scene: keyof typeof S) => S[scene].to - S[scene].from;

const Background: React.FC = () => {
  const f = useCurrentFrame();
  const x = 50 + Math.sin(f / 70) * 18;
  const y = 40 + Math.cos(f / 90) * 12;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${x}% ${y}%, ${C.bg2} 0%, ${C.bg} 55%)`,
      }}
    />
  );
};

// ---------------------------------------------------------------- 1. HOOK
const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const intro = useSpring(0, {damping: 30});
  const scale = 1.16 - 0.1 * intro + f * 0.0006;
  const exit = useExit(dur('hook'), 6);
  const c = (k: CueKey) => at('hook', k);
  return (
    <AbsoluteFill style={{opacity: exit.opacity}}>
      <Photo src="img/1.jpg" scale={scale} origin="50% 38%" />
      <AbsoluteFill
        style={{background: `linear-gradient(180deg, rgba(27,18,25,0) 45%, rgba(27,18,25,0.88) 66%, ${C.bg} 100%)`}}
      />
      <div style={{position: 'absolute', left: 80, top: 1170, ...exit}}>
        <MaskUp at={c('hook_w1')}>
          <H size={118}>{COPY.hook.l1}</H>
        </MaskUp>
        <MaskUp at={c('hook_w2')} style={{marginTop: 18}}>
          <H size={60} weight={700} color={C.sub} style={{letterSpacing: '0.01em'}}>
            {COPY.hook.l2}
          </H>
        </MaskUp>
        <MaskUp at={c('hook_w3')} style={{marginTop: 26}}>
          <H size={118}>{COPY.hook.l3}</H>
        </MaskUp>
        <Punch at={c('hook_w4')} origin="left center">
          <H size={118} color={C.accent}>
            {COPY.hook.l4}
          </H>
        </Punch>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 2. MASALAH
const Drops: React.FC<{start: number}> = ({start}) => {
  const f = useCurrentFrame();
  const drops = [
    {x: 150, y: 520, d: 0, s: 34},
    {x: 900, y: 600, d: 5, s: 26},
    {x: 820, y: 1260, d: 9, s: 40},
    {x: 210, y: 1330, d: 13, s: 24},
  ];
  return (
    <>
      {drops.map((p, i) => {
        const t = f - start - p.d;
        if (t < 0) return null;
        const o = interpolate(t, [0, 6, 40, 60], [0, 0.8, 0.8, 0], clamp);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x,
              top: p.y + t * 2.2,
              width: p.s,
              height: p.s,
              background: C.accent,
              opacity: o,
              borderRadius: '50% 0 50% 50%',
              transform: 'rotate(-45deg)',
            }}
          />
        );
      })}
    </>
  );
};

const Problem: React.FC = () => {
  const f = useCurrentFrame();
  const c = (k: CueKey) => at('prob', k);
  const aOut = interpolate(f, [82, 90], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  return (
    <AbsoluteFill>
      {f < 90 && (
        <AbsoluteFill
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            transform: `translateY(${-aOut * 160}px)`,
            opacity: 1 - aOut,
          }}
        >
          <FadeIn at={c('prob_w1')}>
            <Sub size={52}>{COPY.prob.a1}</Sub>
          </FadeIn>
          <MaskUp at={c('prob_w2')} style={{marginTop: 30}}>
            <H size={200}>{COPY.prob.a2}</H>
          </MaskUp>
          <Punch at={c('prob_w3')}>
            <H size={136} color={C.accent}>
              {COPY.prob.a3}
            </H>
          </Punch>
          <Drops start={c('prob_w3')} />
        </AbsoluteFill>
      )}
      {f >= 90 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          <MaskUp at={c('prob_b1')}>
            <H size={120}>{COPY.prob.b1}</H>
          </MaskUp>
          <Punch at={c('prob_b2')}>
            <H size={300} color={C.accent} style={{marginTop: -10}}>
              {COPY.prob.b2}
            </H>
          </Punch>
          <FadeIn at={c('prob_b3')} style={{marginTop: 40}}>
            <Sub size={50}>{COPY.prob.b3}</Sub>
          </FadeIn>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 3. PRODUK + USP
const Story: React.FC = () => {
  const f = useCurrentFrame();
  const c = (k: CueKey) => at('story', k);
  const reveal = useSpring(c('story_reveal'), {damping: 30, mass: 0.8});
  const toCard = useSpring(c('usp_in'), {damping: 24, mass: 0.9});
  const lerp = (a: number, b: number) => a + (b - a) * toCard;

  // kotak foto: penuh skrin -> kad atas
  const box = {left: lerp(0, 250), top: lerp(0, 140), width: lerp(1080, 580), height: lerp(1920, 800), radius: lerp(0, 44)};
  // punch-in perlahan ke produk, kemudian zoom lagi bila jadi kad supaya botol kekal besar
  const push = interpolate(f, [c('story_reveal'), c('usp_in')], [1.0, 1.12], clamp);
  const inner = push + (1.7 - push) * toCard;

  const lineScale = interpolate(f, [c('story_reveal') - 2, c('story_reveal') + 6], [1, 1.12], clamp);
  const lineOp = interpolate(f, [c('story_reveal') - 2, c('story_reveal') + 6], [1, 0], clamp);
  const lowerOut = interpolate(f, [c('usp_in') - 8, c('usp_in')], [0, 1], clamp);
  const exit = useExit(dur('story'));

  return (
    <AbsoluteFill style={exit}>
      {f >= c('story_reveal') && (
        <div
          style={{
            position: 'absolute',
            left: box.left,
            top: box.top,
            width: box.width,
            height: box.height,
            borderRadius: box.radius,
            overflow: 'hidden',
            clipPath: `circle(${reveal * 75}% at 50% 50%)`,
            boxShadow: toCard > 0.5 ? '0 30px 80px rgba(0,0,0,0.45)' : undefined,
          }}
        >
          <Photo src="img/3.jpg" scale={inner} origin="45.5% 49.5%" />
          {f < c('usp_in') + 2 && (
            <AbsoluteFill
              style={{
                background: `linear-gradient(180deg, rgba(27,18,25,0) 58%, rgba(27,18,25,0.92) 82%)`,
                opacity: (1 - lowerOut) * (f >= c('story_name') ? 1 : 0),
              }}
            />
          )}
        </div>
      )}

      {f < c('story_reveal') + 8 && (
        <AbsoluteFill
          style={{alignItems: 'center', justifyContent: 'center', opacity: lineOp, transform: `scale(${lineScale})`}}
        >
          <Punch at={c('story_line')}>
            <H size={150} style={{textAlign: 'center'}}>
              {COPY.story.line1}
            </H>
            <H size={150} color={C.accent} style={{textAlign: 'center', marginTop: 10}}>
              {COPY.story.line2}
            </H>
          </Punch>
        </AbsoluteFill>
      )}

      {f >= c('story_name') && f < c('usp_in') && (
        <div style={{position: 'absolute', left: 80, top: 1440, opacity: 1 - lowerOut}}>
          <MaskUp at={c('story_name')}>
            <H size={56} color={C.accent} style={{letterSpacing: '0.3em'}}>
              {COPY.story.brand}
            </H>
          </MaskUp>
          <MaskUp at={c('story_name') + 4} style={{marginTop: 8}}>
            <H size={104}>{COPY.story.name}</H>
          </MaskUp>
          <FadeIn at={c('story_name') + 10} style={{marginTop: 14}}>
            <Sub size={42}>{COPY.story.type}</Sub>
          </FadeIn>
        </div>
      )}

      {f >= c('usp_in') && (
        <div style={{position: 'absolute', left: 90, top: 1030}}>
          {[
            [c('usp1'), COPY.story.usp1],
            [c('usp2'), COPY.story.usp2],
          ].map(([t, s]) => (
            <div key={s as string} style={{display: 'flex', alignItems: 'center', gap: 28, marginBottom: 26}}>
              <Check at={t as number} />
              <MaskUp at={(t as number) + 2}>
                <H size={92}>{s}</H>
              </MaskUp>
            </div>
          ))}
          <div style={{height: 3, width: interpolate(f, [c('usp3') - 6, c('usp3') + 6], [0, 900], clamp), background: C.maroon, margin: '18px 0 30px'}} />
          <FadeIn at={c('usp3')}>
            <Sub size={50}>{COPY.story.usp3}</Sub>
          </FadeIn>
          <FadeIn at={c('usp4')} style={{marginTop: 14}}>
            <Sub size={50}>{COPY.story.usp4}</Sub>
          </FadeIn>
        </div>
      )}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 4. 0% ALKOHOL / PARABEN
// Kiraan 100% -> 0% (putih), kemudian "kunci" pada 0% dengan punch berwarna aksen.
const Counter: React.FC<{start: number; lock: number; label: string}> = ({start, lock, label}) => {
  const f = useCurrentFrame();
  const n = Math.round(interpolate(f, [start, lock], [100, 0], {...clamp, easing: Easing.out(Easing.cubic)}));
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', height: 380}}>
      {f >= start && f < lock && <H size={260}>{n}%</H>}
      {f >= lock && (
        <Punch at={lock}>
          <H size={260} color={C.accent}>
            0%
          </H>
        </Punch>
      )}
      <MaskUp at={lock + 2} style={{marginTop: 4}}>
        <H size={96} style={{letterSpacing: '0.06em'}}>
          {label}
        </H>
      </MaskUp>
    </div>
  );
};

const Zero: React.FC = () => {
  const c = (k: CueKey) => at('zero', k);
  const exit = useExit(dur('zero'));
  return (
    <AbsoluteFill style={{alignItems: 'center', paddingTop: 260, ...exit}}>
      <Counter start={c('zero1')} lock={c('zero1_lock')} label={COPY.zero.a} />
      <div style={{height: 120}} />
      <Counter start={c('zero2')} lock={c('zero2_lock')} label={COPY.zero.b} />
      <FadeIn at={c('zero3')} style={{marginTop: 150, width: 860, textAlign: 'center'}}>
        <Sub size={52}>{COPY.zero.c}</Sub>
      </FadeIn>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 5. GAYA HIDUP
const Life: React.FC = () => {
  const f = useCurrentFrame();
  const c = (k: CueKey) => at('life', k);
  const slide = useSpring(0, {damping: 26});
  const exit = useExit(dur('life'));
  return (
    <AbsoluteFill style={exit}>
      <div
        style={{
          position: 'absolute',
          left: 70,
          top: 150,
          width: 940,
          height: 1060,
          borderRadius: 44,
          overflow: 'hidden',
          transform: `translateX(${(1 - slide) * 1100}px) rotate(${(1 - slide) * 6}deg)`,
          boxShadow: '0 30px 80px rgba(0,0,0,0.45)',
        }}
      >
        <Photo src="img/2.jpg" pos="50% 42%" scale={interpolate(f, [0, 90], [1.12, 1.0])} origin="55% 45%" />
      </div>
      <div style={{position: 'absolute', left: 90, top: 1290}}>
        <Punch at={c('life1')} origin="left center">
          <H size={140} color={C.accent}>
            {COPY.life.a}
          </H>
        </Punch>
        <MaskUp at={c('life1') + 6} style={{marginTop: 16}}>
          <H size={76}>{COPY.life.b}</H>
        </MaskUp>
        <FadeIn at={c('life2')} style={{marginTop: 18}}>
          <Sub size={52}>{COPY.life.c}</Sub>
        </FadeIn>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 6. CTA
const Cta: React.FC = () => {
  const f = useCurrentFrame();
  const c = (k: CueKey) => at('cta', k);
  const pop = useSpring(0, {damping: 16, mass: 0.7});
  const pulse = f > c('cta_btn') + 20 ? 1 + Math.sin((f - c('cta_btn') - 20) / 5) * 0.025 : 1;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          left: 190,
          top: 130,
          width: 700,
          height: 900,
          borderRadius: 44,
          overflow: 'hidden',
          transform: `scale(${0.82 + 0.18 * pop})`,
          opacity: Math.min(1, pop * 2),
          boxShadow: '0 30px 80px rgba(0,0,0,0.45)',
        }}
      >
        <Photo src="img/5.jpg" pos="50% 30%" scale={interpolate(f, [0, 105], [1.08, 1.0])} />
      </div>
      <AbsoluteFill style={{alignItems: 'center', top: 1100}}>
        <MaskUp at={c('cta_name')}>
          <H size={84}>{COPY.cta.brand}</H>
        </MaskUp>
        <Punch at={c('cta_btn')} style={{marginTop: 50}}>
          <div
            style={{
              background: C.accent,
              borderRadius: 999,
              padding: '30px 64px',
              transform: `scale(${pulse})`,
            }}
          >
            <H size={58} color={C.bg} style={{letterSpacing: '0.02em'}}>
              {COPY.cta.button}
            </H>
          </div>
        </Punch>
        <FadeIn at={c('cta_tag')} style={{marginTop: 50}}>
          <Sub size={44} style={{fontStyle: 'italic', letterSpacing: '0.04em'}}>
            {COPY.cta.tagline}
          </Sub>
        </FadeIn>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const SCENES: [keyof typeof S, React.FC][] = [
  ['hook', Hook],
  ['prob', Problem],
  ['story', Story],
  ['zero', Zero],
  ['life', Life],
  ['cta', Cta],
];

export const FireaAd: React.FC = () => (
  <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
    <Background />
    {SCENES.map(([k, Comp]) => (
      <Sequence key={k} from={S[k].from} durationInFrames={dur(k)} name={k}>
        <Comp />
      </Sequence>
    ))}
    <Audio src={staticFile('audio/soundtrack.wav')} />
  </AbsoluteFill>
);
