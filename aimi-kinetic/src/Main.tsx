import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad, goldText } from "./theme";
import { Kinetic, WaButton } from "./Kinetic";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);
type Shot = (typeof tl.shots)[number];

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(["700 60px Montserrat", "800 60px Montserrat", "900 60px Montserrat", "700 60px Cinzel"].map((f) => document.fonts.load(f))).then(() => continueRender(h));
  }, [h]);
};

// Emerald field with a faint damask-like pattern, matching the logo artwork.
const Emerald: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, #17533F 0%, ${C.emerald} 45%, ${C.deep} 100%)` }}>
    <AbsoluteFill style={{ opacity: 0.12, background: "radial-gradient(circle at 50% 50%, rgba(246,222,156,0.6) 0 2px, transparent 3px) 0 0/60px 60px, radial-gradient(circle at 50% 50%, rgba(246,222,156,0.35) 0 1px, transparent 2px) 30px 30px/60px 60px" }} />
  </AbsoluteFill>
);

const zoomAt = (sh: Shot, t: number) => {
  const p = (t - sh.s) / (sh.e - sh.s);
  let z = interpolate(p, [0, 1], sh.zoom as number[], { easing: ease, ...clamp });
  for (const pu of tl.punches) {
    const k = interpolate(t, [pu.t, pu.t + 0.12, pu.t + pu.dur, pu.t + pu.dur + 0.3], [0, 1, 1, 0], clamp);
    z *= 1 + pu.amt * k;
  }
  return z;
};

const VideoShot: React.FC<{ sh: Shot }> = ({ sh }) => {
  const f = useCurrentFrame();
  const t = sh.s + f / FPS;
  const z = zoomAt(sh, t);
  const src = sh.kind === "main" ? "main.mp4" : (sh.src as string);
  const from = sh.kind === "main" ? sh.s : (sh.in as number);
  // short whip-in on B-roll entries
  const whip = sh.kind === "video" ? interpolate(f, [0, 5], [1, 0], clamp) : 0;
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(src)}
        startFrom={Math.round(from * FPS)}
        muted
        style={{ width: 1080, height: 1920, objectFit: "cover", transform: `translateX(${whip * 140}px) scale(${z})`, transformOrigin: `50% ${(sh.oy as number) * 100}%`, filter: `blur(${whip * 10}px) saturate(1.06) contrast(1.03)` }}
      />
    </AbsoluteFill>
  );
};

const ImageShot: React.FC<{ sh: Shot }> = ({ sh }) => {
  const f = useCurrentFrame();
  const t = sh.s + f / FPS;
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <Img src={staticFile(sh.src as string)} style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${zoomAt(sh, t)})`, transformOrigin: `50% ${(sh.oy as number) * 100}%` }} />
    </AbsoluteFill>
  );
};

const Sheen: React.FC<{ t: number; at: number; size: number }> = ({ t, at, size }) => {
  if (t < at || t > at + 1.0) return null;
  const x = interpolate(t, [at, at + 1.0], [-0.3, 1.3], { easing: Easing.inOut(Easing.quad), ...clamp });
  return <div style={{ position: "absolute", inset: 0, overflow: "hidden", mixBlendMode: "screen", borderRadius: size }}><div style={{ position: "absolute", top: -size, left: x * size - 80, width: 160, height: size * 3, transform: "rotate(22deg)", background: "linear-gradient(90deg, rgba(255,244,210,0), rgba(255,244,210,0.6), rgba(255,244,210,0))" }} /></div>;
};

const BrandCard: React.FC = () => {
  const t = tl.shots.find((s) => s.kind === "brand")!.s + useCurrentFrame() / FPS;
  const b = tl.brand;
  const lp = interpolate(t, [b.logo, b.logo + 0.45], [0, 1], { easing: Easing.out(Easing.back(1.6)), ...clamp });
  const pre = interpolate(t, [b.pre, b.logo], [0, 0.25], clamp);
  const push = interpolate(t, [b.logo, 7.95], [1, 1.06], clamp);
  const flash = interpolate(t, [b.logo - 0.02, b.logo + 0.05, b.logo + 0.35], [0, 0.7, 0], clamp);
  return (
    <AbsoluteFill>
      <Emerald />
      <div style={{ position: "absolute", left: 90, top: 520, width: 900, height: 900, transform: `scale(${(0.55 + 0.45 * lp) * push}) rotate(${(1 - lp) * -14}deg)`, opacity: Math.max(pre, Math.min(1, lp * 1.5)), filter: lp < 0.01 ? "blur(12px)" : "none" }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 900, height: 900, WebkitMaskImage: "radial-gradient(circle at 50% 48%, #000 52%, transparent 70%)" }} />
        <Sheen t={t} at={b.logo + 0.3} size={900} />
      </div>
      <AbsoluteFill style={{ background: "#FFF6DA", opacity: flash, mixBlendMode: "screen" }} />
    </AbsoluteFill>
  );
};

const TestiCascade: React.FC = () => {
  const cfg = tl.testi;
  const t = cfg.s + useCurrentFrame() / FPS;
  const n = interpolate(t, [cfg.counterFrom, cfg.counterTo], [0, 500], { easing: Easing.out(Easing.cubic), ...clamp });
  const cards = Array.from({ length: cfg.count }, (_, i) => i);
  return (
    <AbsoluteFill>
      <Emerald />
      {cards.map((i) => {
        const at = cfg.s + 0.05 + i * 0.12;
        const p = interpolate(t, [at, at + 0.35], [0, 1], { easing: Easing.out(Easing.back(1.3)), ...clamp });
        const x = 90 + ((i * 197) % 3) * 110 - 60;
        const y = 820 + (i % 4) * 150;
        const r = ((i % 2 ? 1 : -1) * (4 + (i % 3) * 3));
        return (
          <div key={i} style={{ position: "absolute", left: x, top: y + (1 - p) * 900, width: 760, height: 440, borderRadius: 18, overflow: "hidden", border: "5px solid #fff", boxShadow: "0 20px 50px rgba(0,0,0,0.5)", transform: `rotate(${r}deg)`, opacity: Math.min(1, p * 2) }}>
            <Img src={staticFile(`testi/t${i + 1}.jpg`)} style={{ width: 760, height: 440, objectFit: "cover", objectPosition: "50% 0%" }} />
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 0, right: 0, top: 210, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 54, letterSpacing: 10, color: C.white, opacity: interpolate(t, [cfg.s, cfg.s + 0.2], [0, 1], clamp) }}>REKOD LEBIH</div>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 290, lineHeight: 1, letterSpacing: -6, ...goldText, filter: "drop-shadow(0 12px 24px rgba(0,0,0,0.6))" }}>{Math.round(n)}{n >= 499.5 ? "+" : ""}</div>
        <div style={{ marginTop: 6, background: goldGrad, borderRadius: 14, padding: "8px 30px", fontFamily: F.kin, fontWeight: 900, fontSize: 64, color: C.ink, opacity: interpolate(t, [10.0, 10.25], [0, 1], clamp) }}>BUAH RUMAH</div>
      </div>
    </AbsoluteFill>
  );
};

const Pip: React.FC<{ p: (typeof tl.pips)[number] }> = ({ p }) => {
  const f = useCurrentFrame();
  const dur = (p.e - p.s) * FPS;
  const inn = interpolate(f, [0, 8], [0, 1], { easing: Easing.out(Easing.back(1.4)), ...clamp });
  const out = interpolate(f, [dur - 6, dur], [1, 0], clamp);
  const right = p.side === "right";
  return (
    <div style={{ position: "absolute", top: 560, [right ? "right" : "left"]: 50, width: 340, opacity: out, transform: `translateX(${(1 - inn) * (right ? 420 : -420)}px) rotate(${right ? 4 : -4}deg)` }}>
      <div style={{ width: 340, height: 440, borderRadius: 24, overflow: "hidden", border: `5px solid ${C.gold}`, boxShadow: "0 20px 50px rgba(0,0,0,0.5)", background: "#000" }}>
        {p.kind === "image" ? (
          <Img src={staticFile(p.src)} style={{ width: 340, height: 440, objectFit: "cover" }} />
        ) : (
          <OffthreadVideo src={staticFile(p.src)} startFrom={Math.round(((p as { in?: number }).in ?? 0) * FPS)} muted style={{ width: 340, height: 440, objectFit: "cover" }} />
        )}
      </div>
      <div style={{ marginTop: 12, background: C.emerald, border: `2px solid ${C.gold}`, borderRadius: 999, padding: "8px 18px", fontFamily: F.kin, fontWeight: 800, fontSize: 24, color: C.white, textAlign: "center" }}>{p.label}</div>
    </div>
  );
};

const EndCard: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const a = interpolate(t, [0, 0.4], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
  const b = interpolate(t, [0.3, 0.6], [0, 1], clamp);
  const out = interpolate(t, [tl.endCard - 0.3, tl.endCard], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Emerald />
      <div style={{ position: "absolute", left: 190, top: 280, width: 700, height: 700, transform: `scale(${0.7 + 0.3 * a})`, opacity: Math.min(1, a * 1.5) }}>
        <Img src={staticFile("img/logo.png")} style={{ width: 700, height: 700, WebkitMaskImage: "radial-gradient(circle at 50% 48%, #000 52%, transparent 70%)" }} />
        <Sheen t={t} at={0.5} size={700} />
      </div>
      <div style={{ position: "absolute", top: 1030, left: 0, right: 0, textAlign: "center", opacity: b }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 64, letterSpacing: 4, color: C.white }}>UKUR · JAHIT · PASANG</div>
        <div style={{ fontFamily: F.kin, fontWeight: 700, fontSize: 38, letterSpacing: 3, color: C.goldLight, marginTop: 14 }}>100% Bumiputera · 500+ buah rumah</div>
      </div>
      <div style={{ position: "absolute", top: 1260, left: 170 }}>
        <WaButton t={t} at={0.45} label="WhatsApp di bawah" />
      </div>
    </AbsoluteFill>
  );
};

// Darkens the lower third on footage so white type always reads.
const Scrim: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const sh = tl.shots.find((s) => t >= s.s && t < s.e);
  if (!sh || sh.kind === "brand" || sh.kind === "testi" || t >= tl.dialogEnd) return null;
  return <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 48%, rgba(0,0,0,0.25) 60%, rgba(0,0,0,0.62) 100%)" }} />;
};

export const Main: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      {tl.shots.map((sh, i) => (
        <Sequence key={i} from={Math.round(sh.s * FPS)} durationInFrames={Math.round((sh.e - sh.s) * FPS)}>
          {sh.kind === "main" || sh.kind === "video" ? <VideoShot sh={sh} /> : sh.kind === "image" ? <ImageShot sh={sh} /> : sh.kind === "brand" ? <BrandCard /> : <TestiCascade />}
        </Sequence>
      ))}
      <Scrim />
      {tl.pips.map((p, i) => (
        <Sequence key={`p${i}`} from={Math.round(p.s * FPS)} durationInFrames={Math.round((p.e - p.s) * FPS)}>
          <Pip p={p} />
        </Sequence>
      ))}
      <Kinetic />
      <Sequence from={Math.round(tl.dialogEnd * FPS)}>
        <EndCard />
      </Sequence>
      <Audio src={staticFile("dialog.wav")} />
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
