import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import { C, F, goldGrad, goldText } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";
import { Logo, VizEv, VizLayer } from "./Viz";

export type QData = {
  id: string; no: number; title: string; question: string; fps: number; hook: number; clipLen: number;
  dialogEnd: number; endCard: number; total: number; cuts: number[]; beats: never[]; viz: VizEv[];
};

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(["700 60px Montserrat", "800 60px Montserrat", "900 60px Montserrat", "700 60px Cinzel"].map((f) => document.fonts.load(f))).then(() => continueRender(h));
  }, [h]);
};

const Emerald: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, #17533F 0%, ${C.emerald} 45%, ${C.deep} 100%)` }}>
    <AbsoluteFill style={{ opacity: 0.12, background: "radial-gradient(circle at 50% 50%, rgba(246,222,156,0.6) 0 2px, transparent 3px) 0 0/60px 60px" }} />
  </AbsoluteFill>
);

const Tag: React.FC<{ d: QData; small?: boolean }> = ({ d, small }) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 12, background: goldGrad, borderRadius: 999, padding: small ? "8px 20px" : "12px 30px", boxShadow: "0 10px 24px rgba(0,0,0,0.3)" }}>
    <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: small ? 24 : 34, color: C.ink, letterSpacing: 2 }}>QnA #{d.no} · {d.title}</span>
  </div>
);

// Viewer question as a chat bubble (the interviewer's audio is not used).
const Hook: React.FC<{ d: QData }> = ({ d }) => {
  const t = useCurrentFrame() / d.fps;
  const tag = interpolate(t, [0.05, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.6)), ...clamp });
  const bub = interpolate(t, [0.35, 0.7], [0, 1], { easing: Easing.out(Easing.back(1.4)), ...clamp });
  const words = d.question.split(" ");
  const shown = Math.floor(interpolate(t, [0.75, 2.2], [0, words.length], clamp));
  const ans = interpolate(t, [d.hook - 1.1, d.hook - 0.8], [0, 1], clamp);
  const out = interpolate(t, [d.hook - 0.18, d.hook], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Emerald />
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${tag})` }}><Tag d={d} /></div>
      <div style={{ position: "absolute", left: 80, top: 470, width: 920, transform: `translateY(${(1 - bub) * 60}px) scale(${0.9 + 0.1 * bub})`, opacity: Math.min(1, bub * 1.5) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
          <div style={{ width: 70, height: 70, borderRadius: 35, background: "#E5E1D8", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width={44} height={44} viewBox="0 0 48 48"><circle cx={24} cy={17} r={9} fill="#9AA3AE" /><path d="M7 44c0-10 8-15 17-15s17 5 17 15" fill="#9AA3AE" /></svg>
          </div>
          <div style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 30, color: C.goldLight }}>Soalan pelanggan</div>
        </div>
        <div style={{ background: "#fff", borderRadius: "10px 40px 40px 40px", padding: "40px 46px", boxShadow: "0 20px 50px rgba(0,0,0,0.4)" }}>
          <div style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 52, lineHeight: 1.3, color: C.ink }}>
            {words.map((w, i) => <span key={i} style={{ opacity: i < shown ? 1 : 0.08 }}>{w} </span>)}
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", top: 1330, left: 0, right: 0, textAlign: "center", opacity: ans, transform: `translateY(${(1 - ans) * 30}px)` }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 64, ...goldText, filter: "drop-shadow(0 6px 14px rgba(0,0,0,0.5))" }}>JAWAPAN AIMI ↓</div>
      </div>
    </AbsoluteFill>
  );
};

// Jump-cuts: alternate wide/tight framing on every cut so the edit reads as cuts.
const Answer: React.FC<{ d: QData }> = ({ d }) => {
  const f = useCurrentFrame();
  const t = d.hook + f / d.fps;
  let i = 0;
  while (i + 1 < d.cuts.length && d.cuts[i + 1] <= t) i++;
  const s = d.cuts[i];
  const e = i + 1 < d.cuts.length ? d.cuts[i + 1] : d.dialogEnd;
  const tight = i % 2 === 1;
  const base = tight ? [1.5, 1.55] : [1.32, 1.37];
  const z = interpolate((t - s) / Math.max(0.1, e - s), [0, 1], base, { easing: ease, ...clamp }) * interpolate(t - s, [0, 0.12], [i ? 1.035 : 1, 1], clamp);
  const head = interpolate(t, [d.hook, d.hook + 0.4], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
        <OffthreadVideo src={staticFile(`${d.id}/clip.mp4`)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${z})`, transformOrigin: "50% 38%", filter: "saturate(1.05) contrast(1.04)" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.18) 0%, rgba(0,0,0,0) 12%, rgba(0,0,0,0) 48%, rgba(0,0,0,0.32) 60%, rgba(0,0,0,0.62) 100%)" }} />
      <div style={{ position: "absolute", left: 70, top: 150, opacity: head }}><Tag d={d} small /></div>
      <VizLayer viz={d.viz} t={t} />
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{ d: QData }> = ({ d }) => {
  const t = useCurrentFrame() / d.fps;
  const a = interpolate(t, [0, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
  const b = interpolate(t, [0.3, 0.6], [0, 1], clamp);
  const out = interpolate(t, [d.endCard - 0.3, d.endCard], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Emerald />
      <div style={{ position: "absolute", left: 240, top: 300, transform: `scale(${0.7 + 0.3 * a})`, opacity: Math.min(1, a * 1.5) }}><Logo size={600} /></div>
      <div style={{ position: "absolute", top: 960, left: 0, right: 0, textAlign: "center", opacity: b }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 68, color: "#fff" }}>ADA SOALAN LAIN?</div>
        <div style={{ fontFamily: F.kin, fontWeight: 700, fontSize: 36, color: C.goldLight, marginTop: 12 }}>Tanya terus Aimi Curtain</div>
      </div>
      <div style={{ position: "absolute", top: 1180, left: 160 }}><WaButton t={t} at={0.4} label="WhatsApp di bawah" /></div>
    </AbsoluteFill>
  );
};

export const QnA: React.FC<{ d: QData }> = ({ d }) => {
  useFonts();
  const H = Math.round(d.hook * d.fps);
  const END = Math.round(d.dialogEnd * d.fps);
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      <Sequence from={H} durationInFrames={END - H}><Answer d={d} /></Sequence>
      <Kinetic beats={d.beats} />
      <Sequence durationInFrames={H}><Hook d={d} /></Sequence>
      <Sequence from={END}><EndCard d={d} /></Sequence>
      <Sequence from={H}><Audio src={staticFile(`${d.id}/dialog.wav`)} /></Sequence>
      <Audio src={staticFile(`${d.id}/music.wav`)} />
      <Audio src={staticFile(`${d.id}/sfx.wav`)} />
    </AbsoluteFill>
  );
};
