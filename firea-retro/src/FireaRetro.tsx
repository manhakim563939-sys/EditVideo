import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import T from './timeline.json';
import {C} from './theme';
import {COPY} from './copy';
import {AlertIcon, Big, CheckRow, Cursor, Desktop, MenuBar, Photo, Pix, RetroButton, Snap, Typed, Win, snapScale} from './kit';

const SC = Object.fromEntries(T.scenes.map((s) => [s.id, s])) as Record<string, (typeof T.scenes)[number]>;
const cue = (id: string) => (k: string) => (SC[id].cues as unknown as Record<string, number>)[k];

// ---------------------------------------------------------------- 1. HOOK
const Hook: React.FC = () => {
  const c = cue('hook');
  return (
    <>
      <Win x={80} y={150} w={920} h={480} title={COPY.hook.title} open={c('nota')} close={c('close')} pad={40}>
        <Typed text={COPY.hook.lines[0]} at={c('l1')} size={68} caret={false} />
        <Typed text={COPY.hook.lines[1]} at={c('l2')} size={68} caret={false} />
        <Typed text={COPY.hook.lines[2]} at={c('l3')} size={68} color={C.title} />
      </Win>
      <Win x={180} y={700} w={720} h={900} title={COPY.hook.foto} open={c('foto')} close={c('close')}>
        <Photo src="img/1.jpg" pos="50% 42%" />
      </Win>
    </>
  );
};

// ---------------------------------------------------------------- 2. MASALAH
const Problem: React.FC = () => {
  const c = cue('prob');
  return (
    <Win x={100} y={540} w={880} h={680} title={COPY.prob.title} open={c('dlg')} close={c('close')} pad={44}>
      <div style={{display: 'flex', gap: 34, alignItems: 'flex-start'}}>
        <AlertIcon />
        <div>
          <Snap at={c('t1')}>
            <Big size={96}>{COPY.prob.t1[0]}</Big>
            <Big size={96}>{COPY.prob.t1[1]}</Big>
          </Snap>
          <Snap at={c('t2')} style={{marginTop: 30}}>
            <Big size={76} color={C.title}>{COPY.prob.t2}</Big>
          </Snap>
          <Snap at={c('t3')} style={{marginTop: 26, width: 560}}>
            <Big size={40} weight={500}>{COPY.prob.t3}</Big>
          </Snap>
        </div>
      </div>
    </Win>
  );
};

// ---------------------------------------------------------------- 3. PRODUK
const Story: React.FC = () => {
  const c = cue('story');
  return (
    <>
      <Win x={110} y={130} w={860} h={1110} title={COPY.story.title} open={c('foto')} close={c('close')} status={COPY.story.status}>
        <Photo src="img/3.jpg" pos="45% 50%" />
      </Win>
      <Win x={80} y={1290} w={920} h={330} title={COPY.story.panel} open={c('panel')} close={c('close')} pad={36}>
        <Big size={66}>{COPY.story.t1}</Big>
        <Snap at={c('t2')} style={{marginTop: 22}}>
          <Big size={56} color={C.title}>{COPY.story.t2}</Big>
        </Snap>
      </Win>
    </>
  );
};

// ---------------------------------------------------------------- 4. USP (bukti label + senarai semak)
const LabelCrop: React.FC<{w: number; h: number; cx: number; cy: number; cw: number}> = ({w, h, cx, cy, cw}) => {
  const s = w / cw;
  return (
    <div style={{width: w, height: h, position: 'relative', overflow: 'hidden', border: `4px solid ${C.ink}`, boxShadow: `inset 3px 3px 0 ${C.shadow}`}}>
      <Img src={staticFile('img/3.jpg')} style={{position: 'absolute', maxWidth: 'none', width: 1125 * s, left: -cx * s, top: -cy * s}} />
    </div>
  );
};

const Usp: React.FC = () => {
  const c = cue('usp');
  return (
    <Win x={80} y={190} w={920} h={1040} title={COPY.usp.title} open={c('win')} close={c('close')} pad={40}>
      <div style={{display: 'flex', justifyContent: 'center'}}>
        <LabelCrop w={640} h={300} cx={360} cy={1102} cw={296} />
      </div>
      <div style={{marginTop: 34, paddingLeft: 60}}>
        {COPY.usp.items.map((it, i) => (
          <CheckRow key={it} at={c(`c${i + 1}`)} label={it} />
        ))}
      </div>
      <Pix size={38} style={{marginTop: 26, color: C.title}}>{COPY.usp.source}</Pix>
    </Win>
  );
};

// ---------------------------------------------------------------- 5. 0%
const Zero: React.FC = () => {
  const c = cue('zero');
  const box = (k: 'a' | 'b', x: number) => (
    <Win x={x} y={190} w={440} h={560} title={COPY.zero[k].title} open={c(k)} close={c('close')} pad={20}>
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%'}}>
        <Big size={200} color={C.title} weight={900}>0%</Big>
        <Big size={60} weight={700} style={{marginTop: 10}}>{COPY.zero[k].label}</Big>
      </div>
    </Win>
  );
  return (
    <>
      {box('a', 80)}
      {box('b', 560)}
      <Win x={80} y={810} w={920} h={420} title={COPY.zero.noteTitle} open={c('note')} close={c('close')} pad={40}>
        <Big size={64}>{COPY.zero.note[0]}</Big>
        <Big size={64}>{COPY.zero.note[1]}</Big>
        <Pix size={38} style={{marginTop: 22, color: C.title}}>{COPY.zero.source}</Pix>
      </Win>
    </>
  );
};

// ---------------------------------------------------------------- 6. SATU TINDAKAN KURSOR: seret ikon ke beg/
const ICON = {x: 130, y: 450, size: 150};
const cursorAt = (f: number) => {
  const P = T.cursorPath;
  let i = 0;
  while (i < P.length - 1 && f >= P[i + 1].f) i++;
  const a = P[i];
  const b = P[i + 1];
  if (!b || f <= a.f) return {x: a.x, y: a.y};
  const t = (f - a.f) / (b.f - a.f);
  const e = t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
  return {x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e};
};

const Life: React.FC = () => {
  const f = useCurrentFrame();
  const c = cue('life');
  const cur = cursorAt(f);
  const grab = f >= c('grab') && f < c('drop');
  const dropped = f >= c('drop');
  const iconCx = ICON.x + ICON.size / 2;
  const iconCy = ICON.y + ICON.size / 2;
  // ikon ikut kursor dengan offset ketika diseret
  const g0 = cursorAt(c('grab'));
  const ix = grab || dropped ? (dropped ? cursorAt(c('drop')).x : cur.x) - (g0.x - iconCx) : iconCx;
  const iy = grab || dropped ? (dropped ? cursorAt(c('drop')).y : cur.y) - (g0.y - iconCy) : iconCy;
  const iconScale = dropped ? 1 - snapScale(f, c('drop')) : snapScale(f, c('icon'));
  const showCursor = f >= c('cursor') && f < c('close');
  return (
    <>
      <Win x={80} y={130} w={920} h={290} title="nota.txt" open={c('cap')} close={c('close')} pad={26}>
        <Big size={70} color={C.title}>{COPY.life.cap[0]}</Big>
        <Big size={70}>{COPY.life.cap[1]}</Big>
      </Win>
      <Win
        x={300} y={700} w={680} h={840} title={COPY.life.win} open={c('win')} close={c('close')}
        status={dropped ? COPY.life.status : '0 item baharu'}
      >
        <Photo src="img/2.jpg" pos="50% 50%" />
      </Win>
      {iconScale > 0 && f < c('close') && (
        <div
          style={{
            position: 'absolute', left: ix - ICON.size / 2, top: iy - ICON.size / 2, width: ICON.size,
            transform: `scale(${iconScale})`, display: 'flex', flexDirection: 'column', alignItems: 'center',
            opacity: grab ? 0.85 : 1,
          }}
        >
          <div style={{width: ICON.size, height: ICON.size, border: `4px solid ${C.ink}`, overflow: 'hidden', background: C.face, boxShadow: '6px 6px 0 rgba(42,22,34,0.35)'}}>
            <Img src={staticFile('img/3.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '45% 52%', transform: 'scale(2.2)'}} />
          </div>
          <Pix size={34} style={{marginTop: 8, background: grab ? C.title : 'transparent', color: grab ? C.face : C.ink, padding: '0 6px'}}>
            {COPY.life.icon}
          </Pix>
        </div>
      )}
      {showCursor && <Cursor x={cur.x} y={cur.y} down={grab} />}
    </>
  );
};

// ---------------------------------------------------------------- 7. CTA
const Cta: React.FC = () => {
  const f = useCurrentFrame();
  const c = cue('cta');
  const pulse = f > c('btn') + 10 ? 1 + (Math.floor((f - c('btn')) / 10) % 2) * 0.03 : 1; // denyut berperingkat
  return (
    <>
      <Win x={120} y={130} w={840} h={1010} title={COPY.cta.title} open={c('foto')}>
        <Photo src="img/5.jpg" pos="50% 30%" />
      </Win>
      <Win x={80} y={1190} w={920} h={440} title="firea" open={c('panel')} pad={30}>
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26}}>
          <Big size={66}>{COPY.cta.name}</Big>
          {f >= c('btn') && (
            <div style={{transform: `scale(${snapScale(f, c('btn'))})`}}>
              <RetroButton scale={pulse}>{COPY.cta.button}</RetroButton>
            </div>
          )}
          {f >= c('tag') && <Pix size={42} style={{color: C.title}}>{COPY.cta.tag}</Pix>}
        </div>
      </Win>
    </>
  );
};

const COMPS: Record<string, React.FC> = {hook: Hook, prob: Problem, story: Story, usp: Usp, zero: Zero, life: Life, cta: Cta};

export const FireaRetro: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill>
      <Desktop />
      <MenuBar items={COPY.menu} />
      {T.scenes.map((s) => {
        const Comp = COMPS[s.id];
        const el = (
          <Sequence key={s.id} from={from} durationInFrames={s.len} name={s.id}>
            <Comp />
          </Sequence>
        );
        from += s.len;
        return el;
      })}
      <Audio src={staticFile('audio/soundtrack.wav')} />
    </AbsoluteFill>
  );
};
