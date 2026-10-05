import React from "react";
import { AbsoluteFill, Audio, Easing, Img, staticFile, useCurrentFrame } from "remotion";
import TL from "./timeline.json";
import { C, CTA, sans, serif } from "./theme";
import { Blobs, Drop, lerp, PhotoCard, Pill, useSpring, Wipe, Words } from "./kit";

const S = TL.scenes;
const B = TL.beats;
type SceneProps = { f: number };
const inScene = (f: number, s: { from: number; to: number }) => f >= s.from && f < s.to;

// ------------------------------------------------------------------ 1. HOOK
const Hook: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const sweat = sp(f, B.hookSticker3);
  return (
    <AbsoluteFill style={{ background: C.blush }}>
      <Blobs f={f} color={C.rose} opacity={0.45} />
      <div style={{ position: "absolute", top: 150, width: "100%", padding: "0 50px" }}>
        <Words f={f} at={B.hookWord1} stagger={4} size={88} color={C.maroon} text="Bertudung &" />
        <Words f={f} at={B.hookWord1 + 10} stagger={4} size={88} color={C.ink} text="berlengan panjang" />
      </div>
      <PhotoCard src="climb.jpg" f={f} at={0} x={140} y={440} w={800} h={1112} rotate={-2.5} zoom={[1.02, 1.14, 120]} focus="55% 30%" />
      <Pill f={f} at={B.hookSticker1} rotate={-4} style={{ left: 110, top: 1130 }}>Aktif seharian</Pill>
      <Pill f={f} at={B.hookSticker2} rotate={3} bg={C.white} color={C.maroon} style={{ left: 470, top: 1250 }}>Banyak bergerak</Pill>
      <Pill f={f} at={B.hookSticker3} rotate={-2} bg={C.aqua} style={{ left: 170, top: 1370 }}>Banyak berpeluh</Pill>
      {[0, 1, 2].map((i) => {
        const t = f - B.hookSticker3 - 4 - i * 6;
        if (t < 0) return null;
        return <Drop key={i} size={44} style={{ position: "absolute", left: 640 + i * 60, top: 1360 + (t * t) * 0.35, opacity: sweat * Math.max(0, 1 - t / 30) }} />;
      })}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 2. PERSOALAN
const Question: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const q = sp(f, B.qMark, { damping: 9, stiffness: 120 });
  const push = lerp(f, [B.riserStart, S.question.to], [1, 1.07], Easing.in(Easing.quad));
  const ul = lerp(f, [B.qLine2 + 10, B.qLine2 + 24], [0, 1]);
  return (
    <AbsoluteFill style={{ background: C.cream }}>
      <div style={{
        position: "absolute", width: "100%", top: 120, textAlign: "center", fontFamily: serif, fontSize: 1100,
        lineHeight: 1, color: C.rose, opacity: 0.33 * q, transform: `scale(${0.6 + 0.4 * q}) rotate(${8 * Math.sin(f / 25)}deg)`,
      }}>?</div>
      <AbsoluteFill style={{ justifyContent: "center", padding: "0 80px", transform: `scale(${push})` }}>
        <Words f={f} at={B.qLine1} size={96} text="Kenapa ketiak" />
        <div style={{ position: "relative", alignSelf: "center" }}>
          <Words f={f} at={B.qLine2} size={118} color={C.maroon} text="tetap berbau?" />
          <div style={{ position: "absolute", left: 10, bottom: -6, height: 16, borderRadius: 8, background: C.rose, width: `${ul * 96}%`, zIndex: -1 }} />
        </div>
        <div style={{ height: 40 }} />
        <Words f={f} at={B.qLine3} size={56} weight={500} stagger={3} text="walaupun peluh tak nampak di sebalik lengan baju" />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 3. PENERANGAN
const BACT = Array.from({ length: 11 }, (_, i) => {
  const a = (i / 11) * Math.PI * 2 + 0.3;
  return { a, r0: 330 + (i % 3) * 40, r1: 140 + (i % 4) * 22, s: 22 + (i % 3) * 8 };
});

const Explain: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const step = f < B.step2 ? 1 : f < B.step3 ? 2 : 3;
  const at = [B.step1, B.step2, B.step3][step - 1];
  const drop = sp(f, B.step1, { damping: 9, stiffness: 140 });
  const bac = lerp(f, [B.bacteria, B.bacteria + 30], [0, 1], Easing.out(Easing.back(1.3)));
  const smell = lerp(f, [B.bacteria + 22, B.bacteria + 50], [0, 1]);
  const toB3 = lerp(f, [B.step3 - 6, B.step3 + 8], [0, 1], Easing.inOut(Easing.cubic));
  const s3 = sp(f, B.step3 + 4, { damping: 14 });

  const texts: Record<number, { t: string; sub?: string }> = {
    1: { t: "Peluh asalnya *hampir* *tak* *berbau.*" },
    2: { t: "Bau muncul bila *bakteria* di kulit *memecahkan* *peluh.*" },
    3: { t: "Tudung & lengan panjang = *kurang* *aliran* *udara.*", sub: "Kulit kekal lembap lebih lama." },
  };
  return (
    <AbsoluteFill style={{ background: C.cream }}>
      <Blobs f={f} color={C.blush} opacity={0.8} />
      {/* header + progress */}
      <div style={{ position: "absolute", top: 170, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 26 }}>
        <div style={{ fontFamily: sans, fontWeight: 700, fontSize: 40, letterSpacing: 6, color: C.maroon }}>FAHAM PUNCA BAU</div>
        <div style={{ display: "flex", gap: 14 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ width: i === step ? 70 : 22, height: 22, borderRadius: 11, background: i <= step ? C.maroon : C.rose, opacity: i <= step ? 1 : 0.5 }} />
          ))}
        </div>
      </div>

      {/* Ilustrasi 1–2: titisan + bakteria (berkembang dalam babak sama) */}
      <div style={{ position: "absolute", left: 140, top: 360, width: 800, height: 760, opacity: 1 - toB3, transform: `scale(${1 - 0.15 * toB3})` }}>
        <svg width={800} height={760} viewBox="-400 -380 800 760">
          {[0, 1, 2].map((i) => (
            <path key={i} d={`M${-90 + i * 90} -150 q 30 -40 0 -80 q -30 -40 0 -80`} fill="none" stroke={C.odour} strokeWidth={12}
              strokeLinecap="round" strokeDasharray="300" strokeDashoffset={300 * (1 - smell)}
              opacity={smell} transform={`translate(0 ${-12 * Math.sin(f / 8 + i)})`} />
          ))}
          <g transform={`scale(${drop})`}>
            <path d="M0 -190 C0 -190 -120 -20 -120 60 a120 120 0 0 0 240 0 C120 -20 0 -190 0 -190Z"
              fill={bac > 0.6 ? C.odour : C.aqua} opacity={0.95} style={{ transition: "none" }} />
            <ellipse cx={-48} cy={40} rx={22} ry={44} fill="white" opacity={0.45} />
          </g>
          {BACT.map((b, i) => {
            const r = b.r0 + (b.r1 - b.r0) * bac + 8 * Math.sin(f / 5 + i);
            const x = Math.cos(b.a + f / 90) * r, y = Math.sin(b.a + f / 90) * r + 20;
            return (
              <g key={i} transform={`translate(${x} ${y}) scale(${bac})`} opacity={Math.min(1, bac * 2)}>
                {[0, 60, 120, 180, 240, 300].map((d) => (
                  <line key={d} x1={0} y1={0} x2={Math.cos((d * Math.PI) / 180) * b.s * 1.5} y2={Math.sin((d * Math.PI) / 180) * b.s * 1.5} stroke={C.maroon} strokeWidth={4} />
                ))}
                <circle r={b.s} fill={C.rose} stroke={C.maroon} strokeWidth={5} />
              </g>
            );
          })}
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 30, textAlign: "center", fontFamily: sans, fontWeight: 800, fontSize: 52, color: C.odour, opacity: smell, letterSpacing: 4 }}>BAU</div>
      </div>

      {/* Ilustrasi 3: lapisan fabrik memerangkap lembapan, udara terhalang */}
      {f >= B.step3 - 6 && (
        <div style={{ position: "absolute", left: 90, top: 400, width: 900, height: 700, opacity: toB3, transform: `scale(${0.85 + 0.15 * s3})` }}>
          <svg width={900} height={700} viewBox="0 0 900 700">
            <rect x={60} y={560} width={780} height={70} rx={35} fill="#E9C3A8" />
            <text x={450} y={608} textAnchor="middle" fontFamily={sans} fontWeight={700} fontSize={34} fill={C.deep}>KULIT</text>
            <path d="M120 560 C120 260 780 260 780 560" fill={C.maroon} opacity={0.18} stroke={C.maroon} strokeWidth={22} />
            <text x={450} y={300} textAnchor="middle" fontFamily={sans} fontWeight={700} fontSize={34} fill={C.maroon}>FABRIK</text>
            {[0, 1, 2, 3, 4].map((i) => {
              const bob = 10 * Math.sin(f / 7 + i * 1.3);
              return (
                <g key={i} transform={`translate(${250 + i * 100} ${470 + bob}) scale(${s3 * 0.55})`}>
                  <path d="M0 -60 C0 -60 -38 -6 -38 20 a38 38 0 0 0 76 0 C38 -6 0 -60 0 -60Z" fill={C.aqua} />
                </g>
              );
            })}
            {[0, 1, 2].map((i) => {
              const p = ((f - B.step3 + i * 9) % 36) / 36;
              const x = 20 + p * 170;
              return (
                <g key={i} opacity={s3 * (1 - p)} transform={`translate(${x} ${130 + i * 70})`}>
                  <path d="M0 0 h70 l-18 -16 M70 0 l-18 16" stroke={C.aqua} strokeWidth={10} fill="none" strokeLinecap="round" />
                </g>
              );
            })}
            <text x={40} y={90} fontFamily={sans} fontWeight={700} fontSize={36} fill={C.aqua} opacity={s3}>udara</text>
            <g transform={`translate(205 220) scale(${s3})`}>
              <circle r={34} fill={C.white} stroke={C.maroon} strokeWidth={8} />
              <path d="M-14 -14 L14 14 M14 -14 L-14 14" stroke={C.maroon} strokeWidth={9} strokeLinecap="round" />
            </g>
          </svg>
        </div>
      )}

      {/* Teks langkah */}
      <div key={step} style={{ position: "absolute", top: 1170, left: 80, right: 80, display: "flex", gap: 30, alignItems: "flex-start" }}>
        <div style={{
          flex: "0 0 auto", width: 96, height: 96, borderRadius: 48, background: C.maroon, color: C.white, fontFamily: sans,
          fontWeight: 800, fontSize: 42, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${sp(f, at)})`,
        }}>0{step}</div>
        <div>
          <Words f={f} at={at + 2} size={60} weight={700} stagger={2} align="left" lh={1.18} text={texts[step].t} />
          {texts[step].sub && <Words f={f} at={at + 26} size={46} weight={500} stagger={2} align="left" style={{ marginTop: 18 }} text={texts[step].sub} />}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 4. DEODORANT vs ANTIPERSPIRANT
const Card: React.FC<{ f: number; at: number; y: number; title: string; verb: string; noun: string; icon: React.ReactNode; color: string }> =
  ({ f, at, y, title, verb, noun, icon, color }) => {
    const sp = useSpring();
    const p = sp(f, at, { damping: 14, stiffness: 150 });
    return (
      <div style={{
        position: "absolute", left: 90, top: y, width: 900, height: 330, background: C.white, borderRadius: 44,
        boxShadow: "0 24px 50px rgba(74,15,36,0.14)", display: "flex", alignItems: "center", gap: 44, padding: "0 56px",
        opacity: Math.min(1, p * 2), transform: `translateX(${(1 - p) * (at === B.cardA ? -300 : 300)}px)`,
      }}>
        <div style={{ width: 170, height: 170, borderRadius: 85, background: color, display: "flex", alignItems: "center", justifyContent: "center", flex: "0 0 auto" }}>{icon}</div>
        <div style={{ fontFamily: sans }}>
          <div style={{ fontWeight: 700, fontSize: 40, letterSpacing: 3, color: C.maroon }}>{title}</div>
          <div style={{ fontWeight: 600, fontSize: 64, color: C.ink, lineHeight: 1.1 }}>{verb} <span style={{ fontWeight: 800, color }}>{noun}</span></div>
        </div>
      </div>
    );
  };

const Compare: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const plus = sp(f, B.plus, { damping: 9 });
  return (
    <AbsoluteFill style={{ background: C.cream }}>
      <Blobs f={f} color={C.blush} opacity={0.9} />
      <div style={{ position: "absolute", top: 170, width: "100%" }}>
        <Words f={f} at={S.compare.from + 2} size={58} weight={700} color={C.maroon} text="Bezanya ramai tak tahu:" />
      </div>
      <Card f={f} at={B.cardA} y={330} title="DEODORANT" verb="Kawal" noun="bau" color={C.odour}
        icon={<svg width={110} height={110} viewBox="0 0 110 110">{[0, 1, 2].map((i) => <path key={i} d={`M${25 + i * 30} 95 q 14 -20 0 -40 q -14 -20 0 -40`} stroke="white" strokeWidth={9} fill="none" strokeLinecap="round" />)}</svg>} />
      <Card f={f} at={B.cardB} y={760} title="ANTIPERSPIRANT" verb="Kurangkan" noun="peluh" color={C.aqua}
        icon={<Drop size={86} color={C.white} />} />
      <div style={{
        position: "absolute", left: 470, top: 640, width: 140, height: 140, borderRadius: 70, background: C.maroon, color: C.white,
        fontFamily: sans, fontWeight: 800, fontSize: 96, lineHeight: "140px", textAlign: "center", transform: `scale(${plus}) rotate(${(1 - plus) * 90}deg)`,
        boxShadow: "0 12px 30px rgba(74,15,36,0.3)",
      }}>+</div>
      <div style={{ position: "absolute", top: 1180, width: "100%", padding: "0 80px" }}>
        <Words f={f} at={B.plus + 4} size={64} weight={600} text="Aktif seharian?" />
        <Words f={f} at={B.plus + 14} size={76} text="Pilih yang buat *kedua-duanya.*" />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 5. CONTOH (produk)
const CHIPS = ["Lindung bau & peluh", "Cepat kering", "Tak melekit", "0% Alkohol", "0% Paraben"];

const Example: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const hero = sp(f, B.product, { damping: 12, stiffness: 110 });
  const out = lerp(f, [B.life - 4, B.life + 8], [0, 1], Easing.inOut(Easing.cubic));
  const chipAt = [B.chip1, B.chip2, B.chip3, B.chip4, B.chip5];
  return (
    <AbsoluteFill style={{ background: C.blush }}>
      <Blobs f={f} color={C.white} opacity={0.55} />
      {/* A: hero produk */}
      {f < B.life + 8 && (
        <AbsoluteFill style={{ opacity: 1 - out, transform: `translateX(${-200 * out}px)` }}>
          <div style={{ position: "absolute", top: 160, width: "100%", textAlign: "center" }}>
            <Words f={f} at={B.product + 2} size={104} weight={400} family={serif} color={C.maroon} stagger={4} text="Firea Celeste Musk" />
            <div style={{ fontFamily: sans, fontWeight: 600, fontSize: 40, color: C.ink, marginTop: 14, opacity: lerp(f, [B.product + 12, B.product + 22], [0, 1]) }}>
              Deodorant Roll-on + Antiperspirant
            </div>
          </div>
          <div style={{ position: "absolute", left: 140, top: 1390, width: 400, height: 60, borderRadius: "50%", background: "rgba(74,15,36,0.18)", filter: "blur(16px)", opacity: hero }} />
          <Img src={staticFile("product_cutout.png")} style={{
            position: "absolute", left: 150, top: 440, height: 980,
            transform: `translateY(${(1 - hero) * 900}px) rotate(${(1 - hero) * -12 + Math.sin(f / 30) * 1.2}deg)`,
          }} />
          {CHIPS.map((c, i) => {
            const p = sp(f, chipAt[i], { damping: 12, stiffness: 200 });
            const zero = c.startsWith("0%");
            return (
              <div key={c} style={{
                position: "absolute", left: 590, top: 580 + i * 150, fontFamily: sans, fontWeight: 700, fontSize: 40,
                background: zero ? C.maroon : C.white, color: zero ? C.white : C.maroon, padding: "22px 34px", borderRadius: 999,
                boxShadow: "0 12px 26px rgba(74,15,36,0.16)", whiteSpace: "nowrap",
                opacity: Math.min(1, p * 2), transform: `translateX(${(1 - p) * 120}px) scale(${0.8 + 0.2 * p})`,
              }}>{c}</div>
            );
          })}
        </AbsoluteFill>
      )}
      {/* B: dalam kehidupan sebenar */}
      {f >= B.life - 4 && (
        <AbsoluteFill style={{ opacity: out }}>
          <div style={{ position: "absolute", top: 160, width: "100%", padding: "0 70px" }}>
            <Words f={f} at={B.life + 2} size={84} color={C.maroon} text="Saiz 50ml," />
            <Words f={f} at={B.life + 8} size={60} weight={600} text="mudah dibawa ke mana-mana" />
          </div>
          <PhotoCard src="bag.jpg" f={f} at={B.life + 4} x={70} y={450} w={520} h={726} rotate={-5} zoom={[1, 1.07, 90]} focus="45% 45%" />
          <PhotoCard src="woman.jpg" f={f} at={B.life + 12} x={540} y={560} w={460} h={818} rotate={4} zoom={[1, 1.06, 90]} focus="40% 35%" />
          <Pill f={f} at={B.lifeChip} size={46} rotate={-2} style={{ left: 160, top: 1420 }}>Sesuai untuk kegunaan harian</Pill>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 6. TAKEAWAY + CTA
const Takeaway: React.FC<SceneProps> = ({ f }) => {
  const sp = useSpring();
  const logo = sp(f, B.endcard, { damping: 14, stiffness: 120 });
  const cta = sp(f, B.endcard + 10);
  return (
    <AbsoluteFill style={{ background: C.deep }}>
      <Blobs f={f} color={C.maroon} opacity={0.9} />
      <div style={{ position: "absolute", top: 250, width: "100%", padding: "0 70px" }}>
        <div style={{ textAlign: "center", fontFamily: sans, fontWeight: 700, fontSize: 38, letterSpacing: 8, color: C.rose, marginBottom: 26, opacity: lerp(f, [B.takeaway, B.takeaway + 8], [0, 1]) }}>INGAT</div>
        <Words f={f} at={B.takeaway + 2} size={84} color={C.white} text="Kawal peluh," />
        <Words f={f} at={B.takeaway + 10} size={84} color={C.white} text="kawal bau —" />
        <Words f={f} at={B.takeaway + 20} size={84} color={C.white} accent={C.rose} text="*yakin* seharian." />
      </div>
      <Img src={staticFile("logo_white.png")} style={{
        position: "absolute", left: 300, top: 820, width: 480, opacity: logo, transform: `scale(${0.8 + 0.2 * logo})`,
      }} />
      <div style={{ position: "absolute", top: 1180, width: "100%", display: "flex", flexDirection: "column", alignItems: "center", gap: 26, opacity: Math.min(1, cta * 1.5), transform: `translateY(${(1 - cta) * 40}px)` }}>
        <div style={{ fontFamily: sans, fontWeight: 700, fontSize: 56, background: C.white, color: C.maroon, padding: "22px 52px", borderRadius: 999 }}>{CTA.line}</div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ KOMPOSISI
export const FireaAd: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.cream }}>
      <Audio src={staticFile("audio/mix.wav")} />
      {inScene(f, S.hook) && <Hook f={f} />}
      {inScene(f, S.question) && <Question f={f} />}
      {inScene(f, S.explain) && <Explain f={f} />}
      {inScene(f, S.compare) && <Compare f={f} />}
      {inScene(f, S.example) && <Example f={f} />}
      {inScene(f, S.takeaway) && <Takeaway f={f} />}
      <Wipe f={f} at={S.question.from} color={C.maroon} kind="up" />
      <Wipe f={f} at={S.explain.from} color={C.rose} kind="iris" />
      <Wipe f={f} at={S.compare.from} color={C.maroon} kind="left" />
      <Wipe f={f} at={S.example.from} color={C.rose} kind="iris" />
      <Wipe f={f} at={S.takeaway.from} color={C.deep} kind="up" />
    </AbsoluteFill>
  );
};
