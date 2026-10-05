import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, Easing} from 'remotion';
import T from './timeline.json';
import {C} from './theme';
import {COPY} from './copy';
import {
  Body, Crop, Draw, Head, Layer, Note, Paper, Print, Strip, Tape,
  arrow, clamp, mapCrop, roughRect, scribbleEllipse, useDrift, useExit,
} from './kit';

type CueKey = keyof typeof T.cues;
type SceneKey = keyof typeof T.scenes;
const S = T.scenes;
const dur = (s: SceneKey) => S[s].to - S[s].from;
const cue = (s: SceneKey) => (k: CueKey) => T.cues[k] - S[s].from;

// Tag kertas kecil untuk anotasi marker supaya kekal terbaca atas foto.
const Tag: React.FC<{at: number; children: React.ReactNode; size?: number}> = ({at, children, size = 44}) => (
  <div style={{background: C.card, padding: '10px 22px 14px', boxShadow: '0 6px 10px rgba(40,25,10,0.25)'}}>
    <Note at={at + 2} size={size}>
      {children}
    </Note>
  </div>
);

// ---------------------------------------------------------------- 1. HOOK (4s)
const CROP1: Crop = {src: 'img/1.jpg', sw: 720, cx: 0, cy: 110, cw: 720};
const Hook: React.FC = () => {
  const c = cue('hook');
  const d = useDrift(dur('hook'));
  const m = mapCrop(CROP1, 700);
  const [bx, by] = m(215, 735); // bawah botol dalam tangan
  return (
    <AbsoluteFill style={useExit(dur('hook'))}>
      <Layer at={c('hook_print')} x={150} y={110} rot={-2.5} drift={d}>
        <Print crop={CROP1} w={700} h={960} seed={11}>
          <div style={{position: 'absolute', left: 10, top: 800, transform: 'rotate(-5deg)'}}>
            {/* Tag dalam koordinat foto */}
            <TagIn at={c('hook_tag')} />
          </div>
          <Draw at={c('hook_arrow')} d={arrow(150, 792, bx + 4, by + 14, -0.2)} />
        </Print>
      </Layer>
      <Tape at={c('hook_tape')} x={400} y={88} rot={-4} w={230} seed={5} />
      <Layer at={c('hook_h1')} x={90} y={1180} depth={0.5} drift={d} from={[-60, 0]}>
        <Head size={92}>{COPY.hook.h1}</Head>
      </Layer>
      <Layer at={c('hook_h2')} x={90} y={1290} depth={0.5} drift={d} from={[-60, 0]}>
        <Head size={88}>{COPY.hook.h2}</Head>
      </Layer>
      <Layer at={c('hook_h3')} x={90} y={1400} depth={0.5} drift={d} from={[-60, 0]}>
        <Head size={92} color={C.accent}>
          {COPY.hook.h3}
        </Head>
      </Layer>
    </AbsoluteFill>
  );
};
const TagIn: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  return <Tag at={at}>{COPY.hook.tag}</Tag>;
};

// ---------------------------------------------------------------- 2. MASALAH (5s)
const drop = (x: number, y: number, s: number) =>
  `M${x},${y} C${x + s * 0.6},${y + s * 0.9} ${x + s * 0.55},${y + s * 1.5} ${x},${y + s * 1.5} C${x - s * 0.55},${y + s * 1.5} ${x - s * 0.6},${y + s * 0.9} ${x},${y}`;

const Problem: React.FC = () => {
  const c = cue('prob');
  const d = useDrift(dur('prob'));
  return (
    <AbsoluteFill style={useExit(dur('prob'))}>
      <Layer at={c('prob_s1')} x={60} y={600} rot={-2} drift={d}>
        <Strip seed={21} w={960} h={200}>
          <Head size={96}>{COPY.prob.s1}</Head>
        </Strip>
      </Layer>
      <div style={{position: 'absolute', left: 0, top: 0}}>
        <Draw at={c('prob_drops')} d={drop(860, 440, 70)} len={10} />
        <Draw at={c('prob_drops') + 5} d={drop(950, 500, 50)} len={10} />
        <Draw at={c('prob_drops') + 9} d={drop(790, 520, 40)} len={10} />
      </div>
      <Layer at={c('prob_s2')} x={200} y={850} rot={2.5} depth={1.5} drift={d} from={[80, 40]}>
        <Strip seed={22} w={700} h={210} bg={C.accent}>
          <Head size={112} color={C.card}>
            {COPY.prob.s2}
          </Head>
        </Strip>
      </Layer>
      <div style={{position: 'absolute', left: 120, top: 1150}}>
        <Note at={c('prob_note')} size={46} len={18}>
          {COPY.prob.note}
        </Note>
        <Draw at={c('prob_note') + 16} d="M0,78 C220,66 520,90 830,72" len={10} width={6} />
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 3. PRODUK (5s)
const CROP3: Crop = {src: 'img/3.jpg', sw: 1125, cx: 120, cy: 320, cw: 880};
const Story: React.FC = () => {
  const c = cue('story');
  const d = useDrift(dur('story'));
  const m = mapCrop(CROP3, 780);
  const [lx, ly] = m(508, 1135); // tengah label
  return (
    <AbsoluteFill style={useExit(dur('story'))}>
      <Layer at={c('story_print')} x={130} y={100} rot={2} drift={d} from={[0, 120]}>
        <Print crop={CROP3} w={780} h={1100} seed={31}>
          <Draw at={c('story_circle')} d={scribbleEllipse(lx, ly, 175, 225, 3)} len={14} />
          <Draw at={c('story_tag') + 4} d={arrow(560, 150, lx + 40, ly - 240, 0.2)} len={10} />
          <div style={{position: 'absolute', left: 330, top: 40, transform: 'rotate(3deg)'}}>
            <StoryTag at={c('story_tag')} />
          </div>
        </Print>
      </Layer>
      <Tape at={c('story_tape')} x={110} y={140} rot={-38} w={200} seed={7} />
      <Tape at={c('story_tape') + 3} x={800} y={1150} rot={-35} w={200} seed={8} />
      <Layer at={c('story_strip')} x={80} y={1290} rot={-1.5} depth={0.5} drift={d} from={[-80, 0]}>
        <Strip seed={32} w={720} h={270}>
          <div>
            <Head size={104}>{COPY.story.strip[0]}</Head>
            <Head size={104} color={C.accent}>
              {COPY.story.strip[1]}
            </Head>
          </div>
        </Strip>
      </Layer>
      <Layer at={c('story_strip') + 10} x={100} y={1600} depth={0.5} drift={d} from={[0, 30]}>
        <Body size={40}>{COPY.story.sub}</Body>
      </Layer>
    </AbsoluteFill>
  );
};
const StoryTag: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  return f < at ? null : <Tag at={at}>{COPY.story.tag}</Tag>;
};

// ---------------------------------------------------------------- 4. BUKTI LABEL (9.5s, 2 idea)
const CROP4: Crop = {src: 'img/3.jpg', sw: 1125, cx: 362, cy: 1012, cw: 278};
const Evidence: React.FC = () => {
  const f = useCurrentFrame();
  const c = cue('evid');
  const d = useDrift(dur('evid'));
  const m = mapCrop(CROP4, 700);
  const [ox, oy] = m(380, 1150); // baris "Odour & Wetness Protection / Quick dry"
  const [ax, ay] = m(422, 1269); // bulatan 0% Alcohol
  const [px, py] = m(504, 1269); // bulatan 0% Paraben
  const [ex, ey] = m(585, 1196); // hujung kanan-bawah baris "Quick dry | Non sticky"
  const k = 700 / CROP4.cw;
  const swap = c('evid_swap');
  const out = interpolate(f, [swap, swap + 8], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
  const part1 = {transform: `translateX(${-out * 1150}px)`};
  return (
    <AbsoluteFill style={useExit(dur('evid'))}>
      <Layer at={c('evid_print')} x={170} y={110} rot={1.2} drift={d} from={[0, 120]}>
        <Print crop={CROP4} w={700} h={900} seed={41}>
          {f < swap + 6 && (
            <div style={{opacity: 1 - out}}>
              <Draw at={c('evid_box')} d={roughRect(ox - 10, oy - 6, ex - ox + 10, ey - oy + 6)} len={14} />
              <div style={{position: 'absolute', left: ox, top: ey + 14, transform: 'rotate(-2deg)'}}>
                <Note at={c('evid_box') + 12} size={40}>
                  {COPY.evid.box}
                </Note>
              </div>
            </div>
          )}
          <Draw at={c('evid_c1')} d={scribbleEllipse(ax, ay, 41 * k, 38 * k, 5)} len={12} />
          <Draw at={c('evid_c2')} d={scribbleEllipse(px, py, 41 * k, 38 * k, 6)} len={12} />
        </Print>
      </Layer>
      <Tape at={c('evid_tape')} x={420} y={86} rot={3} w={220} seed={9} />

      {f < swap + 8 && (
        <div style={{position: 'absolute', inset: 0, ...part1}}>
          <Layer at={c('evid_strip')} x={70} y={1120} rot={-1.5} depth={0.5} drift={d} from={[-80, 0]}>
            <Strip seed={42} w={720} h={250}>
              <div>
                <Head size={96}>{COPY.evid.strip[0]}</Head>
                <Head size={96} color={C.accent}>
                  {COPY.evid.strip[1]}
                </Head>
              </div>
            </Strip>
          </Layer>
          <div style={{position: 'absolute', left: 110, top: 1420}}>
            <Note at={c('evid_note')} size={50} len={16}>
              {COPY.evid.note}
            </Note>
          </div>
        </div>
      )}

      <Layer at={c('evid_strip2')} x={70} y={1120} rot={1.5} depth={0.5} drift={d} from={[80, 0]}>
        <Strip seed={43} w={720} h={250} bg={C.accent}>
          <div>
            <Head size={96} color={C.card}>
              {COPY.evid.strip2[0]}
            </Head>
            <Head size={96} color={C.card}>
              {COPY.evid.strip2[1]}
            </Head>
          </div>
        </Strip>
      </Layer>
      <div style={{position: 'absolute', left: 90, top: 1420}}>
        <Note at={c('evid_note2')} size={46} len={18}>
          {COPY.evid.note2}
        </Note>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- 5. GAYA HIDUP (3.5s)
const CROP2: Crop = {src: 'img/2.jpg', sw: 768, cx: 0, cy: 120, cw: 768};
const Life: React.FC = () => {
  const c = cue('life');
  const d = useDrift(dur('life'));
  const m = mapCrop(CROP2, 800);
  const [bx, by] = m(330, 345); // bahu botol
  return (
    <AbsoluteFill style={useExit(dur('life'))}>
      <Layer at={c('life_print')} x={120} y={130} rot={-2} drift={d} from={[120, 60]}>
        <Print crop={CROP2} w={800} h={860} seed={51}>
          <div style={{position: 'absolute', left: 20, top: 40, transform: 'rotate(-3deg)'}}>
            <LifeTag at={c('life_tag')} />
          </div>
          <Draw at={c('life_tag') + 6} d={arrow(200, 132, bx - 10, by - 10, 0.25)} len={10} />
        </Print>
      </Layer>
      <Tape at={c('life_tape')} x={760} y={110} rot={35} w={200} seed={12} />
      <Layer at={c('life_strip')} x={80} y={1110} rot={-1.2} depth={0.5} drift={d} from={[-80, 0]}>
        <Strip seed={52} w={880} h={250}>
          <div>
            <Head size={96} color={C.accent}>
              {COPY.life.strip[0]}
            </Head>
            <Head size={96}>{COPY.life.strip[1]}</Head>
          </div>
        </Strip>
      </Layer>
    </AbsoluteFill>
  );
};
const LifeTag: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  return f < at ? null : <Tag at={at} size={44}>{COPY.life.tag}</Tag>;
};

// ---------------------------------------------------------------- 6. CTA (3s)
const CROP5: Crop = {src: 'img/5.jpg', sw: 768, cx: 60, cy: 40, cw: 650};
const Cta: React.FC = () => {
  const c = cue('cta');
  const d = useDrift(dur('cta'));
  return (
    <AbsoluteFill>
      <Layer at={c('cta_print')} x={222} y={110} rot={-2} drift={d}>
        <Print crop={CROP5} w={600} h={760} seed={61} />
      </Layer>
      <Tape at={c('cta_print') + 6} x={440} y={86} rot={-3} w={210} seed={13} />
      <Layer at={c('cta_name')} x={0} y={990} depth={0.5} drift={d} from={[0, 40]} style={{width: 1080}}>
        <Head size={84} style={{textAlign: 'center'}}>
          {COPY.cta.name}
        </Head>
      </Layer>
      <Layer at={c('cta_btn')} x={0} y={1130} depth={0.5} drift={d} from={[0, -30]} style={{width: 1080, display: 'flex', justifyContent: 'center'}}>
        <div
          style={{
            border: `7px solid ${C.accent}`,
            padding: '20px 44px',
            transform: 'rotate(-3deg)',
            background: 'rgba(251,248,241,0.6)',
          }}
        >
          <Head size={62} color={C.accent} style={{letterSpacing: '0.01em'}}>
            {COPY.cta.button}
          </Head>
        </div>
      </Layer>
      <div style={{position: 'absolute', left: 0, top: 1310, width: 1080, display: 'flex', justifyContent: 'center'}}>
        <Note at={c('cta_tag')} size={50} len={16} color={C.ink}>
          {COPY.cta.tag}
        </Note>
      </div>
    </AbsoluteFill>
  );
};

const SCENES: [SceneKey, React.FC][] = [
  ['hook', Hook],
  ['prob', Problem],
  ['story', Story],
  ['evid', Evidence],
  ['life', Life],
  ['cta', Cta],
];

export const FireaScrapbook: React.FC = () => (
  <AbsoluteFill>
    <Paper />
    {SCENES.map(([k, Comp]) => (
      <Sequence key={k} from={S[k].from} durationInFrames={dur(k)} name={k}>
        <Comp />
      </Sequence>
    ))}
    <Audio src={staticFile('audio/soundtrack.wav')} />
  </AbsoluteFill>
);
