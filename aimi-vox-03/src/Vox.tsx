import React from "react";
import { AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from "remotion";
import tl from "./timeline.json";
import { C } from "./theme";

const FPS = tl.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const V = {
  paper: "#EEE5D2",
  ink: "#1C1A17",
  marker: "#FFD84A",
  red: "#D2452E",
  blue: "#3D6FA8",
  serif: "'Playfair Display', serif",
  type: "'Special Elite', monospace",
};
const pop = (t: number, at: number, d = 0.25) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.out(Easing.back(1.8)), ...clamp });
const draw = (t: number, at: number, d = 0.5) => interpolate(t, [at, at + d], [0, 1], { easing: Easing.inOut(Easing.cubic), ...clamp });
// stop-motion jitter: changes 12 times a second, deterministic per element
const jit = (t: number, k: number, amp = 2) => {
  const q = Math.floor(t * 12);
  const r = Math.sin(q * 12.9898 + k * 78.233) * 43758.5453;
  return (r - Math.floor(r) - 0.5) * 2 * amp;
};

export const Paper: React.FC<{ grid?: boolean }> = ({ grid = true }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Img src={staticFile("img/paper.jpg")} style={{ width: 1080, height: 1920 }} />
      {grid && <AbsoluteFill style={{ backgroundImage: "linear-gradient(rgba(61,111,168,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(61,111,168,0.10) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />}
      <AbsoluteFill style={{ backgroundImage: `url(${staticFile("img/grain.png")})`, backgroundSize: "540px 960px", backgroundPosition: `${(f * 37) % 540}px ${(f * 53) % 960}px`, opacity: 0.07, mixBlendMode: "multiply" }} />
    </AbsoluteFill>
  );
};

export const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ backgroundImage: `url(${staticFile("img/grain.png")})`, backgroundSize: "540px 960px", backgroundPosition: `${(f * 37) % 540}px ${(f * 53) % 960}px`, opacity: 0.06, mixBlendMode: "overlay" }} />;
};

const Tape: React.FC<{ x: number; y: number; r: number; w?: number }> = ({ x, y, r, w = 150 }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: 44, background: "rgba(240,228,190,0.75)", boxShadow: "0 2px 4px rgba(0,0,0,0.15)", transform: `rotate(${r}deg)`, clipPath: "polygon(3% 0, 97% 4%, 100% 50%, 96% 100%, 2% 96%, 0 50%)" }} />
);

// Host as a taped photo print (top-right) while the explainer plays.
export const HostCard: React.FC<{ t: number; s: number }> = ({ t, s }) => {
  const p = pop(t, s, 0.3);
  const W = 360;
  const H = 450;
  const sc = 0.62;
  const fx = tl.face.x * sc;
  const fy = tl.face.y * sc;
  return (
    <div style={{ position: "absolute", left: 660 + jit(t, 1, 1.5), top: 140 + jit(t, 2, 1.5), transform: `rotate(${3 + jit(t, 3, 0.3)}deg) scale(${0.6 + 0.4 * p})`, opacity: Math.min(1, p * 1.6) }}>
      <div style={{ width: W, height: H, padding: 12, paddingBottom: 54, background: "#FBF8F1", boxShadow: "0 14px 30px rgba(0,0,0,0.28)" }}>
        <div style={{ width: W - 24, height: H - 66, overflow: "hidden", position: "relative", background: "#000" }}>
          <OffthreadVideo src={staticFile("main.mp4")} startFrom={Math.round(s * FPS)} muted style={{ position: "absolute", width: 1080 * sc, height: 1920 * sc, left: (W - 24) / 2 - fx, top: (H - 66) / 2 - fy, filter: "saturate(0.9) contrast(1.05)" }} />
        </div>
        <div style={{ fontFamily: V.type, fontSize: 24, color: V.ink, marginTop: 10, textAlign: "center" }}>Aimi Curtain</div>
      </div>
      <Tape x={W / 2 - 75} y={-22} r={-4} />
    </div>
  );
};

const Kicker: React.FC<{ t: number; s: number; text: string }> = ({ t, s, text }) => {
  const n = Math.floor(interpolate(t, [s + 0.15, s + 0.15 + text.length * 0.03], [0, text.length], clamp));
  return (
    <div style={{ position: "absolute", left: 70, top: 250, width: 540, transform: `rotate(-2deg)` }}>
      <div style={{ display: "inline-block", background: V.ink, color: V.paper, fontFamily: V.type, fontSize: 30, padding: "10px 18px", lineHeight: 1.3 }}>{text.slice(0, n)}{n < text.length ? "▌" : ""}</div>
    </div>
  );
};

type Line = { t: string; at: number; big?: boolean };
const parse = (s: string) => {
  const out: { w: string; hl: boolean }[] = [];
  let on = false;
  for (const tok of s.split(" ")) {
    let w = tok;
    if (w.startsWith("*")) { on = true; w = w.slice(1); }
    const close = w.endsWith("*");
    if (close) w = w.slice(0, -1);
    out.push({ w, hl: on });
    if (close) on = false;
  }
  return out;
};

// Serif headline; *words* get a highlighter stroke swept behind them.
const Headline: React.FC<{ t: number; lines: Line[] }> = ({ t, lines }) => (
  <div style={{ position: "absolute", left: 70, top: 660, width: 940 }}>
    {lines.map((l, i) => {
      const p = interpolate(t, [l.at, l.at + 0.2], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
      const words = parse(l.t);
      const size = Math.min(l.big ? 150 : 76, Math.floor(920 / (l.t.replace(/\*/g, "").length * 0.74)));
      return (
        <div key={i} style={{ opacity: p, transform: `translateY(${(1 - p) * 26}px)`, whiteSpace: "nowrap", lineHeight: 1.12 }}>
          {words.map((w, j) => {
            const hp = draw(t, l.at + 0.15 + j * 0.05, 0.3);
            return (
              <span key={j} style={{ position: "relative", display: "inline-block", marginRight: size * 0.24 }}>
                {w.hl && <span style={{ position: "absolute", left: -8, right: -8, top: "18%", bottom: "8%", background: V.marker, transform: `scaleX(${hp}) skewX(-8deg) rotate(-1deg)`, transformOrigin: "0% 50%", opacity: 0.9, zIndex: 0 }} />}
                <span style={{ position: "relative", zIndex: 1, fontFamily: V.serif, fontWeight: 900, fontSize: size, color: V.ink, letterSpacing: -1 }}>{w.w}</span>
              </span>
            );
          })}
        </div>
      );
    })}
  </div>
);

const Label: React.FC<{ t: number; at: number; text: string; x: number; y: number; r?: number; red?: boolean }> = ({ t, at, text, x, y, r = -3, red }) => {
  const p = pop(t, at, 0.25);
  return (
    <div style={{ position: "absolute", left: x + jit(t, x, 1.2), top: y + jit(t, y, 1.2), transform: `rotate(${r}deg) scale(${p})`, opacity: Math.min(1, p * 1.5), background: red ? V.red : "#FBF8F1", color: red ? "#fff" : V.ink, fontFamily: V.type, fontSize: 34, padding: "8px 16px", boxShadow: "0 6px 14px rgba(0,0,0,0.22)", whiteSpace: "nowrap" }}>{text}</div>
  );
};

const Circle: React.FC<{ t: number; at: number; cx: number; cy: number; rx: number; ry: number }> = ({ t, at, cx, cy, rx, ry }) => (
  <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none" }}>
    <ellipse cx={cx} cy={cy} rx={rx} ry={ry} fill="none" stroke={V.red} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray="1.05 1" strokeDashoffset={1 - draw(t, at, 0.45)} transform={`rotate(-6 ${cx} ${cy})`} />
  </svg>
);

const Arrow: React.FC<{ t: number; at: number; x1: number; y1: number; x2: number; y2: number; color?: string }> = ({ t, at, x1, y1, x2, y2, color = V.red }) => {
  const d = draw(t, at, 0.35);
  const a = Math.atan2(y2 - y1, x2 - x1);
  const mx = (x1 + x2) / 2 + Math.sin(a) * 40;
  const my = (y1 + y2) / 2 - Math.cos(a) * 40;
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0, pointerEvents: "none" }}>
      <path d={`M${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}`} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - d} />
      {d > 0.95 && <path d={`M${x2} ${y2} l ${-26 * Math.cos(a - 0.5)} ${-26 * Math.sin(a - 0.5)} M${x2} ${y2} l ${-26 * Math.cos(a + 0.5)} ${-26 * Math.sin(a + 0.5)}`} stroke={color} strokeWidth={7} strokeLinecap="round" />}
    </svg>
  );
};

// ---------------------------------------------------------------- diagrams
const Money: React.FC<{ t: number }> = ({ t }) => {
  const coins = [3.7, 3.95, 4.2, 4.45, 4.7];
  const fill = interpolate(t, [3.8, 5.0], [0.08, 0.6], clamp);
  return (
    <div style={{ position: "absolute", left: 330 + jit(t, 7), top: 1080 + jit(t, 8) }}>
      <svg width={420} height={480} viewBox="0 0 420 480">
        <rect x={60} y={120} width={300} height={340} rx={40} fill="rgba(255,255,255,0.35)" stroke={V.ink} strokeWidth={8} />
        <rect x={70} y={120 + 330 * (1 - fill)} width={280} height={330 * fill} rx={30} fill="#D9B35E" opacity={0.85} />
        <rect x={90} y={80} width={240} height={50} rx={12} fill="#FBF8F1" stroke={V.ink} strokeWidth={8} />
      </svg>
      {coins.map((at, i) => {
        const y = interpolate(t, [at, at + 0.3], [-260, 300 - i * 20], { easing: Easing.in(Easing.quad), ...clamp });
        return t >= at ? <div key={i} style={{ position: "absolute", left: 160 + (i % 3) * 22, top: y, width: 90, height: 90, borderRadius: 45, background: "radial-gradient(circle at 35% 30%, #FFF1B8, #D9B35E 55%, #9C7428)", border: `5px solid ${V.ink}`, opacity: t > at + 0.32 ? 0 : 1 }} /> : null;
      })}
      <Label t={t} at={4.5} text="+ JIMAT" x={330} y={140} r={6} />
    </div>
  );
};

const Aircond: React.FC<{ t: number }> = ({ t }) => {
  const rp = pop(t, 6.3, 0.3);
  const flick = t > 6.36 && t < 6.6 ? (Math.floor(t * 20) % 2 ? 0.3 : 1) : 1;
  const merc = interpolate(t, [7.6, 9.0], [0.82, 0.74], clamp);
  const load = interpolate(t, [7.6, 9.0], [0.02, 0.22], clamp);
  return (
    <>
      <div style={{ position: "absolute", left: 110 + jit(t, 11), top: 1090 + jit(t, 12), transform: `rotate(-6deg) scale(${rp})`, opacity: Math.min(1, rp * 1.5) }}>
        <div style={{ width: 300, height: 470, borderRadius: 60, background: "#F7F4EC", border: `7px solid ${V.ink}`, boxShadow: "0 14px 30px rgba(0,0,0,0.25)", padding: 30 }}>
          <div style={{ height: 170, borderRadius: 16, background: "#BFD3C2", border: `5px solid ${V.ink}`, display: "flex", alignItems: "center", justifyContent: "center", gap: 6, opacity: flick }}>
            <span style={{ fontFamily: "'Montserrat', sans-serif", fontWeight: 900, fontSize: 110, color: V.ink }}>16</span>
            <span style={{ fontFamily: "'Montserrat', sans-serif", fontWeight: 800, fontSize: 40, color: V.ink, marginTop: -50 }}>°C</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 40 }}>
            {[0, 1, 2].map((i) => <div key={i} style={{ width: 62, height: 62, borderRadius: 31, background: i === 1 ? V.blue : "#DDD6C6", border: `5px solid ${V.ink}` }} />)}
          </div>
        </div>
      </div>
      <div style={{ position: "absolute", left: 640 + jit(t, 13), top: 1080 + jit(t, 14), opacity: interpolate(t, [7.5, 7.7], [0, 1], clamp) }}>
        <svg width={120} height={440} viewBox="0 0 120 440">
          <rect x={35} y={10} width={50} height={340} rx={25} fill="#FBF8F1" stroke={V.ink} strokeWidth={7} />
          <rect x={47} y={20 + 320 * (1 - merc)} width={26} height={320 * merc} rx={13} fill={V.red} />
          <circle cx={60} cy={385} r={45} fill={V.red} stroke={V.ink} strokeWidth={7} />
        </svg>
      </div>
      <div style={{ position: "absolute", left: 440, top: 1590, width: 540, opacity: interpolate(t, [7.6, 7.8], [0, 1], clamp) }}>
        <div style={{ fontFamily: V.type, fontSize: 30, color: V.ink, marginBottom: 8 }}>rasa sejuk... {Math.round(load * 100)}%</div>
        <div style={{ height: 30, border: `5px solid ${V.ink}`, background: "#FBF8F1" }}><div style={{ width: `${load * 100}%`, height: "100%", background: V.blue }} /></div>
      </div>
      <Circle t={t} at={8.1} cx={700} cy={1300} rx={110} ry={260} />
    </>
  );
};

const Bill: React.FC<{ t: number }> = ({ t }) => {
  const cp = pop(t, 9.05, 0.3);
  const bp = interpolate(t, [10.76, 11.05], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const bars = [0.25, 0.35, 0.45, 0.62, 0.95];
  return (
    <>
      <div style={{ position: "absolute", left: 80 + jit(t, 21), top: 1090 + jit(t, 22), transform: `rotate(-5deg) scale(${cp})`, opacity: Math.min(1, cp * 1.5) }}>
        <div style={{ width: 400, background: "#FBF8F1", border: `6px solid ${V.ink}`, boxShadow: "0 12px 26px rgba(0,0,0,0.22)" }}>
          <div style={{ background: V.red, color: "#fff", fontFamily: V.type, fontSize: 32, textAlign: "center", padding: "10px 0" }}>HUJUNG BULAN</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 6, padding: 16 }}>
            {Array.from({ length: 35 }, (_, i) => <div key={i} style={{ height: 36, border: `2px solid rgba(28,26,23,0.35)`, background: i === 33 ? "rgba(210,69,46,0.25)" : "transparent" }} />)}
          </div>
        </div>
      </div>
      <Circle t={t} at={9.6} cx={80 + 16 + 5.5 * 54 + 30} cy={1090 + 70 + 4 * 42 + 40} rx={46} ry={34} />
      <div style={{ position: "absolute", left: 540 + jit(t, 23), top: 1060 + (1 - bp) * 700 + jit(t, 24), transform: "rotate(4deg)" }}>
        <div style={{ width: 420, background: "#FFFFFF", border: `6px solid ${V.ink}`, padding: 24, boxShadow: "0 14px 30px rgba(0,0,0,0.25)", clipPath: "polygon(0 0, 100% 0, 100% 96%, 92% 100%, 84% 96%, 76% 100%, 68% 96%, 60% 100%, 52% 96%, 44% 100%, 36% 96%, 28% 100%, 20% 96%, 12% 100%, 4% 96%, 0 100%)" }}>
          <div style={{ fontFamily: V.type, fontSize: 36, color: V.ink }}>BIL ELEKTRIK</div>
          <div style={{ height: 3, background: V.ink, margin: "10px 0 20px" }} />
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16, height: 300 }}>
            {bars.map((h, i) => {
              const g = interpolate(t, [11.0 + i * 0.08, 11.25 + i * 0.08], [0, 1], { easing: Easing.out(Easing.back(1.5)), ...clamp });
              return <div key={i} style={{ flex: 1, height: `${h * 100 * g}%`, background: i === 4 ? V.red : "#9BA7B4", border: `4px solid ${V.ink}` }} />;
            })}
          </div>
          <div style={{ height: 40 }} />
        </div>
      </div>
      <Arrow t={t} at={11.3} x1={600} y1={1480} x2={950} y2={1110} />
      <Label t={t} at={11.5} text="MELAMBUNG!" x={600} y={1600} r={-8} red />
    </>
  );
};

const Sun: React.FC<{ t: number; haba: number; cahaya: number }> = ({ t, haba, cahaya }) => {
  const s0 = 20.3;
  const sp = pop(t, s0 + 0.1, 0.35);
  const cur = interpolate(t, [20.4, 20.9], [0, 1], { easing: Easing.out(Easing.cubic), ...clamp });
  const rays = [0, 1, 2, 3, 4];
  return (
    <>
      {/* sun */}
      <div style={{ position: "absolute", left: 60, top: 1050, transform: `scale(${sp}) rotate(${(t - s0) * 25}deg)`, opacity: Math.min(1, sp * 1.5) }}>
        <svg width={240} height={240} viewBox="0 0 240 240">
          {Array.from({ length: 12 }, (_, i) => <line key={i} x1={120} y1={18} x2={120} y2={52} stroke="#E8A33A" strokeWidth={10} strokeLinecap="round" transform={`rotate(${i * 30} 120 120)`} />)}
          <circle cx={120} cy={120} r={55} fill="#F6C343" stroke={V.ink} strokeWidth={7} />
        </svg>
      </div>
      {/* rays travelling to the curtain and stopping there */}
      {rays.map((i) => {
        const ph = ((t - s0) * 0.9 + i / rays.length) % 1;
        const x = 250 + ph * 300;
        const y = 1170 + i * 70;
        return <div key={i} style={{ position: "absolute", left: x, top: y, width: 80, height: 12, borderRadius: 6, background: i % 2 ? "#E8A33A" : "#F6C343", opacity: (t > s0 + 0.4 ? 1 : 0) * Math.min(1, (1 - ph) * 4), border: `3px solid ${V.ink}` }} />;
      })}
      {/* window + thick curtain */}
      <div style={{ position: "absolute", left: 600, top: 1040, width: 30, height: 560, background: "#C9D9E6", border: `6px solid ${V.ink}` }} />
      <div style={{ position: "absolute", left: 630, top: 1030, width: 150 * cur, height: 580, background: "repeating-linear-gradient(90deg, #0F3D30 0 22px, #17533F 22px 44px)", border: `6px solid ${V.ink}`, boxShadow: "8px 10px 0 rgba(0,0,0,0.15)" }} />
      {/* cool room side */}
      <div style={{ position: "absolute", left: 800, top: 1040, width: 220, height: 560, background: "rgba(61,111,168,0.12)", border: `4px dashed rgba(28,26,23,0.4)` }} />
      <div style={{ position: "absolute", left: 830, top: 1520, fontFamily: V.type, fontSize: 28, color: V.ink }}>dalam rumah</div>
      <Label t={t} at={20.6} text="KAIN TEBAL" x={580} y={960} r={-4} />
      <Label t={t} at={haba} text="✕ HABA" x={250} y={1660} r={-5} red />
      <Label t={t} at={cahaya} text="✕ CAHAYA" x={560} y={1690} r={4} red />
    </>
  );
};

export const VoxScene: React.FC<{ type: string; s: number }> = ({ type, s }) => {
  const t = s + useCurrentFrame() / FPS;
  const cfg = (tl.vox as Record<string, { kicker: string; lines: Line[]; haba?: number; cahaya?: number }>)[type];
  const slide = interpolate(t - s, [0, 0.22], [1, 0], { easing: Easing.out(Easing.cubic), ...clamp });
  return (
    <AbsoluteFill style={{ transform: `translateX(${slide * 1080}px)` }}>
      <Paper />
      <Kicker t={t} s={s} text={cfg.kicker} />
      <HostCard t={t} s={s} />
      <Headline t={t} lines={cfg.lines} />
      {type === "money" && <Money t={t} />}
      {type === "aircond" && <Aircond t={t} />}
      {type === "bill" && <Bill t={t} />}
      {type === "sun" && <Sun t={t} haba={cfg.haba!} cahaya={cfg.cahaya!} />}
    </AbsoluteFill>
  );
};

// Real Aimi Curtain jobs as a taped collage with typewriter call-outs.
export const PhotoCollage: React.FC<{ s: number; e: number }> = ({ s, e }) => {
  const t = s + useCurrentFrame() / FPS;
  const srcs = ["img/hasil1.jpg", "img/hasil2.jpg", "img/hasil3.jpg"];
  const per = (e - s) / srcs.length;
  return (
    <AbsoluteFill>
      <Paper />
      {srcs.map((src, i) => {
        const at = s + i * per;
        const p = pop(t, at, 0.3);
        if (t < at) return null;
        const r = [-4, 3, -2][i];
        return (
          <div key={src} style={{ position: "absolute", left: 90 + i * 14 + jit(t, 40 + i), top: 230 + i * 16 + jit(t, 50 + i), transform: `rotate(${r}deg) scale(${0.85 + 0.15 * p})`, opacity: Math.min(1, p * 1.5) }}>
            <div style={{ width: 900, height: 1200, padding: 16, background: "#FBF8F1", boxShadow: "0 18px 40px rgba(0,0,0,0.3)" }}>
              <Img src={staticFile(src)} style={{ width: 868, height: 1168, objectFit: "cover", transform: `scale(${interpolate(t, [at, at + per], [1.0, 1.06], clamp)})` }} />
            </div>
            <Tape x={360} y={-20} r={-3} w={180} />
          </div>
        );
      })}
      {tl.photoLabels.map((l) => (
        <React.Fragment key={l.t}>
          <Arrow t={t} at={l.at + 0.15} x1={l.x + 160} y1={l.y + 70} x2={l.ax} y2={l.ay} color={V.marker} />
          <Label t={t} at={l.at} text={l.t} x={l.x} y={l.y} r={-3} />
        </React.Fragment>
      ))}
      <div style={{ position: "absolute", left: 600, top: 1170, transform: `rotate(-10deg) scale(${pop(t, tl.photoStamp, 0.3) * (2 - interpolate(t, [tl.photoStamp, tl.photoStamp + 0.15], [1, 0], clamp))})`, opacity: interpolate(t, [tl.photoStamp, tl.photoStamp + 0.08], [0, 1], clamp) }}>
        <div style={{ width: 300, height: 300, borderRadius: 150, overflow: "hidden", border: `8px solid ${C.gold}`, boxShadow: "0 14px 30px rgba(0,0,0,0.4)" }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 300, height: 300, transform: "scale(1.04)" }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// B-roll room that physically dims at "redup" and gets snow at "cepat sejuk".
export const Room: React.FC<{ s: number; e: number; inn: number }> = ({ s, inn }) => {
  const f = useCurrentFrame();
  const t = s + f / FPS;
  const dim = interpolate(t, [25.9, 26.6], [1, 0.62], clamp);
  const cool = interpolate(t, [27.5, 28.0], [0, 1], clamp);
  const flakes = Array.from({ length: 26 }, (_, i) => i);
  const merc = interpolate(t, [27.6, 28.6], [0.8, 0.3], { easing: Easing.out(Easing.cubic), ...clamp });
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <OffthreadVideo src={staticFile("broll/ruang-kelabu.mp4")} startFrom={Math.round(inn * FPS)} muted style={{ width: 1080, height: 1920, objectFit: "cover", filter: `brightness(${dim}) saturate(${0.8 + 0.2 * dim}) hue-rotate(${cool * -12}deg)`, transform: `scale(${1 + (t - s) * 0.015})` }} />
      <AbsoluteFill style={{ background: "rgba(80,140,220,0.18)", opacity: cool }} />
      {flakes.map((i) => {
        const x = (i * 157) % 1080;
        const y = ((t - 27.5) * (120 + (i % 5) * 30) + i * 97) % 1100 + 150;
        return <div key={i} style={{ position: "absolute", left: x + Math.sin(t * 2 + i) * 20, top: y, fontSize: 30 + (i % 3) * 12, color: "#fff", opacity: cool * 0.85, textShadow: "0 2px 6px rgba(0,0,0,0.3)" }}>❄</div>;
      })}
      <div style={{ position: "absolute", right: 80, top: 260, opacity: cool }}>
        <svg width={110} height={400} viewBox="0 0 120 440">
          <rect x={35} y={10} width={50} height={340} rx={25} fill="#FBF8F1" stroke={V.ink} strokeWidth={7} />
          <rect x={47} y={20 + 320 * (1 - merc)} width={26} height={320 * merc} rx={13} fill={V.blue} />
          <circle cx={60} cy={385} r={45} fill={V.blue} stroke={V.ink} strokeWidth={7} />
        </svg>
      </div>
      <Grain />
    </AbsoluteFill>
  );
};
