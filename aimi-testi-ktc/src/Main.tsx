import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C, F, goldGrad } from "./theme";
import { Kinetic } from "./Kinetic";
import { VizLayer } from "./Viz";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);
type Seg = (typeof tl.segs)[number];

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

const Footage: React.FC<{ g: Seg }> = ({ g }) => {
  const f = useCurrentFrame();
  const p = f / FPS / (g.e - g.s);
  const zr = (g as { zoom?: number[] }).zoom ?? [1, 1.05];
  const z = interpolate(p, [0, 1], zr, { easing: ease, ...clamp });
  const whip = interpolate(f, [0, 5], [1, 0], clamp);
  const style: React.CSSProperties = { width: 1080, height: 1920, objectFit: "cover", transform: `translateX(${whip * 120}px) scale(${z})`, filter: `blur(${whip * 8}px) saturate(1.06) contrast(1.03)` };
  if (g.kind === "wide") {
    // landscape photo: framed print over a blurred copy of itself
    return (
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
        <Img src={staticFile(g.src as string)} style={{ ...style, filter: "blur(30px) brightness(0.6)", transform: "scale(1.2)" }} />
        <div style={{ position: "absolute", left: 40, top: 640, width: 1000, padding: 14, background: "#fff", boxShadow: "0 20px 50px rgba(0,0,0,0.5)", transform: `rotate(-2deg) scale(${0.9 + 0.1 * interpolate(f, [0, 8], [0, 1], clamp)})` }}>
          <Img src={staticFile(g.src as string)} style={{ width: 972, height: 547, objectFit: "cover", transform: `scale(${1 + p * 0.06})` }} />
        </div>
      </AbsoluteFill>
    );
  }
  if (g.kind === "main") {
    const gm = g as unknown as { ox: number; oy: number; s: number };
    return (
      <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
        <OffthreadVideo src={staticFile("main.mp4")} startFrom={Math.round(gm.s * FPS)} muted style={{ ...style, transform: `scale(${z})`, transformOrigin: `${gm.ox * 100}% ${gm.oy * 100}%`, filter: "saturate(1.05) contrast(1.05)" }} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      {g.kind === "image" ? <Img src={staticFile(g.src as string)} style={style} /> : <OffthreadVideo src={staticFile(g.src as string)} startFrom={Math.round(((g as { in?: number }).in ?? 0) * FPS)} muted style={style} />}
    </AbsoluteFill>
  );
};

// "Sana kayangan, sini marhaen": finished curtains (top) vs the room still being fitted (bottom, from the main video).
const Split: React.FC<{ g: Seg }> = ({ g }) => {
  const f = useCurrentFrame();
  const t = g.s + f / FPS;
  const sp = tl.split;
  const top = (g as unknown as { top: { src: string; in: number } }).top;
  const wipe = interpolate(f, [0, 8], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const lab = (at: number) => interpolate(t, [at, at + 0.3], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 952, overflow: "hidden", transform: `translateY(${(1 - wipe) * -952}px)` }}>
        <OffthreadVideo src={staticFile(top.src)} startFrom={Math.round(top.in * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `translateY(-430px) scale(${1.02 + f * 0.0008})`, filter: "saturate(1.15) brightness(1.06)" }} />
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle at 70% 30%, rgba(255,230,160,0.35), rgba(0,0,0,0) 60%)" }} />
      </div>
      <div style={{ position: "absolute", left: 0, top: 968, width: 1080, height: 952, overflow: "hidden", transform: `translateY(${(1 - wipe) * 952}px)` }}>
        <OffthreadVideo src={staticFile("main.mp4")} startFrom={Math.round(g.s * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: "scale(1.5)", transformOrigin: "45% 66%", filter: "saturate(0.35) brightness(0.85) contrast(0.95)" }} />
      </div>
      <div style={{ position: "absolute", left: 0, top: 952, width: 1080, height: 16, background: goldGrad }} />
      <div style={{ position: "absolute", left: 60, top: 250, transform: `scale(${lab(sp.kayangan)})`, transformOrigin: "0% 50%" }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 40, color: "#fff", letterSpacing: 6, textShadow: "0 3px 10px rgba(0,0,0,0.6)" }}>SANA SEKARANG</div>
        <div style={{ display: "inline-block", marginTop: 6, background: goldGrad, borderRadius: 16, padding: "6px 26px", boxShadow: "0 12px 26px rgba(0,0,0,0.4)" }}><span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 96, color: C.ink }}>KAYANGAN</span></div>
      </div>
      <div style={{ position: "absolute", left: 60, top: 640, transform: `scale(${lab(sp.kaya)})`, transformOrigin: "0% 50%", background: C.emerald, border: `4px solid ${C.gold}`, borderRadius: 16, padding: "10px 24px" }}>
        <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 44, color: C.goldLight }}>NAMPAK MACAM ORANG KAYA</span>
      </div>
      <div style={{ position: "absolute", left: 60, top: 1060, transform: `scale(${lab(sp.marhaen)})`, transformOrigin: "0% 50%" }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 40, color: "#fff", letterSpacing: 6, textShadow: "0 3px 10px rgba(0,0,0,0.7)" }}>SINI</div>
        <div style={{ display: "inline-block", marginTop: 6, background: "rgba(255,255,255,0.92)", borderRadius: 16, padding: "6px 26px" }}><span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 96, color: "#555" }}>MARHAEN</span></div>
      </div>
    </AbsoluteFill>
  );
};

const Tag: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const p = interpolate(t, [0.1, 0.45], [0, 1], { easing: Easing.out(Easing.back(1.6)), ...clamp }) * interpolate(t, [3.7, 4.0], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 150, transform: `scale(${p})`, transformOrigin: "0% 50%", background: goldGrad, borderRadius: 999, padding: "8px 22px", boxShadow: "0 10px 24px rgba(0,0,0,0.3)" }}>
      <span style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 24, color: C.ink, letterSpacing: 2 }}>REVIEW PELANGGAN · KTC</span>
    </div>
  );
};

const Sheen: React.FC<{ t: number; at: number; size: number }> = ({ t, at, size }) => {
  if (t < at || t > at + 1.0) return null;
  const x = interpolate(t, [at, at + 1.0], [-0.3, 1.3], clamp);
  return <div style={{ position: "absolute", inset: "15%", borderRadius: "50%", overflow: "hidden", mixBlendMode: "screen" }}><div style={{ position: "absolute", top: -size, left: x * size - 80, width: 160, height: size * 3, transform: "rotate(22deg)", background: "linear-gradient(90deg, rgba(255,244,210,0), rgba(255,244,210,0.6), rgba(255,244,210,0))" }} /></div>;
};

// Closing shot: full-screen finished-curtain B-roll with animated logo, sparkles and the closing line.
export const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const pop = (at: number, d = 0.35) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
  const logo = pop(0.05, 0.45);
  const rays = interpolate(t, [0.2, 0.9], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const l1 = pop(0.45);
  const l2 = pop(0.7);
  const cta = pop(0.95, 0.4);
  const out = interpolate(t, [tl.endCard - 0.25, tl.endCard], [1, 0], clamp);
  const sparks = Array.from({ length: 22 }, (_, i) => i);
  return (
    <AbsoluteFill style={{ opacity: out, overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("broll/b4.mp4")} startFrom={Math.round(2.0 * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", transform: `scale(${1.06 + t * 0.05})`, filter: "saturate(1.15) brightness(0.9)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(8,38,30,0.55) 0%, rgba(0,0,0,0.05) 30%, rgba(0,0,0,0.1) 55%, rgba(8,38,30,0.85) 100%)" }} />
      {sparks.map((i) => {
        const x = (i * 211) % 1080;
        const y = 1700 - ((t * (260 + (i % 5) * 60) + i * 137) % 1500);
        const o = (0.4 + 0.6 * Math.abs(Math.sin(t * 5 + i))) * interpolate(t, [0.1, 0.4], [0, 1], clamp);
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 8 + (i % 3) * 4, height: 8 + (i % 3) * 4, borderRadius: 2, background: C.goldLight, opacity: o, transform: `rotate(45deg)`, boxShadow: `0 0 12px ${C.gold}` }} />;
      })}
      <div style={{ position: "absolute", left: 340, top: 260, width: 400, height: 400 }}>
        {Array.from({ length: 16 }, (_, i) => {
          const ang = (i / 16) * Math.PI * 2;
          const r = 150 + 120 * rays;
          return <div key={i} style={{ position: "absolute", left: 200 + Math.cos(ang) * r - 4, top: 200 + Math.sin(ang) * r - 22, width: 8, height: 44, borderRadius: 4, background: C.goldLight, opacity: (1 - rays) * 0.9, transform: `rotate(${(ang * 180) / Math.PI + 90}deg)` }} />;
        })}
        <div style={{ position: "absolute", inset: 0, borderRadius: 200, overflow: "hidden", border: `6px solid ${C.gold}`, boxShadow: "0 20px 50px rgba(0,0,0,0.55)", transform: `scale(${logo}) rotate(${(1 - logo) * -60}deg)`, opacity: Math.min(1, logo * 1.5) }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 400, height: 400, transform: "scale(1.05)" }} />
          <Sheen t={t} at={0.6} size={400} />
        </div>
      </div>
      <div style={{ position: "absolute", top: 1010, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ fontFamily: F.kin, fontWeight: 900, fontSize: 76, color: "#fff", textShadow: "0 6px 18px rgba(0,0,0,0.6)", transform: `translateY(${(1 - l1) * 60}px) scale(${0.8 + 0.2 * l1})`, opacity: Math.min(1, l1 * 1.5) }}>DARI BUMI KE LANGIT</div>
        <div style={{ fontFamily: F.kin, fontWeight: 800, fontSize: 40, color: C.goldLight, marginTop: 14, textShadow: "0 4px 12px rgba(0,0,0,0.6)", transform: `translateY(${(1 - l2) * 40}px)`, opacity: Math.min(1, l2 * 1.5) }}>Servis bagus · Pemasangan tangkas</div>
      </div>
      <div style={{ position: "absolute", top: 1250, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${cta * (1 + 0.035 * Math.max(0, Math.sin((t - 0.95) * 7)))})`, opacity: Math.min(1, cta * 1.5) }}>
        <div style={{ position: "relative", background: goldGrad, borderRadius: 999, padding: "24px 56px", border: "5px solid #fff", boxShadow: "0 16px 40px rgba(0,0,0,0.5)", overflow: "hidden" }}>
          <span style={{ position: "relative", fontFamily: F.kin, fontWeight: 900, fontSize: 60, color: C.ink }}>JOM, AIMI CURTAIN BANTU!</span>
          <div style={{ position: "absolute", top: -40, bottom: -40, width: 90, left: interpolate(t, [1.3, 2.0], [-120, 1000], clamp), transform: "rotate(20deg)", background: "linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.7), rgba(255,255,255,0))" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Main: React.FC = () => {
  useFonts();
  const END = Math.round(tl.dialogEnd * FPS);
  return (
    <AbsoluteFill style={{ backgroundColor: C.deep }}>
      {tl.segs.map((g, i) => (
        <Sequence key={i} from={Math.round(g.s * FPS)} durationInFrames={Math.round((g.e - g.s) * FPS)}>
          {g.kind === "split" ? <Split g={g} /> : <Footage g={g} />}
        </Sequence>
      ))}
      <Sequence durationInFrames={END}>
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.05) 16%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.3) 56%, rgba(0,0,0,0.65) 100%)" }} />
        <Tag />
        <VizLayer />
      </Sequence>
      <Kinetic />
      <Audio src={staticFile("dialog.wav")} />
      <Audio src={staticFile("music.wav")} />
      <Audio src={staticFile("sfx.wav")} />
    </AbsoluteFill>
  );
};
