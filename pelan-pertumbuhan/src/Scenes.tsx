import React from "react";
import { Easing, Img, interpolate, staticFile } from "remotion";
import { C, F, goldFill, goldText } from "./theme";
import { clamp, draw, Eyebrow, Icon, In, pop, rise, Ring, Scene } from "./ui";
import { GoalViz, Viz } from "./Viz";

type P = { sc: Scene; t: number };
const cue = (sc: Scene, k: string) => sc.cueT[k];

// Light sweep across gold text/logo
const Sheen: React.FC<{ t: number; at: number; w: number; h: number }> = ({ t, at, w, h }) => {
  const x = interpolate(t, [at, at + 1.1], [-0.4, 1.4], { easing: Easing.inOut(Easing.quad), ...clamp });
  if (t < at || t > at + 1.2) return null;
  return (
    <div style={{ position: "absolute", inset: 0, width: w, height: h, overflow: "hidden", pointerEvents: "none", mixBlendMode: "screen" }}>
      <div style={{ position: "absolute", top: -h, left: x * w - 60, width: 120, height: h * 3, transform: "rotate(20deg)", background: "linear-gradient(90deg, rgba(255,240,200,0), rgba(255,240,200,0.55), rgba(255,240,200,0))" }} />
    </div>
  );
};

export const IntroScene: React.FC<P> = ({ sc, t }) => {
  const logo = pop(t, 1.15, 0.7);
  const glow = interpolate(t, [1.1, 1.5, 3.5], [0, 1, 0.35], clamp);
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "relative", width: 300, height: 300, transform: `scale(${0.6 + 0.4 * logo}) rotate(${(1 - logo) * -12}deg)`, opacity: Math.min(1, logo * 1.5) }}>
        <div style={{ position: "absolute", inset: -60, borderRadius: 300, background: `radial-gradient(circle, rgba(243,217,152,${0.35 * glow}), rgba(0,0,0,0) 65%)` }} />
        <Img src={staticFile("img/logo.png")} style={{ width: 300, height: 300, borderRadius: 150, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
        <Sheen t={t} at={1.6} w={300} h={300} />
      </div>
      <In t={t} at={cue(sc, "pelan")} style={{ marginTop: 40 }}>
        <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 30, letterSpacing: 16, color: C.cream, textAlign: "center" }}>PELAN PERTUMBUHAN</div>
      </In>
      <In t={t} at={cue(sc, "pelan") + 0.3}>
        <div style={{ position: "relative", fontFamily: F.serif, fontWeight: 600, fontSize: 104, letterSpacing: 6, ...goldText, textAlign: "center", lineHeight: 1.15 }}>Aimi Curtain</div>
      </In>
      <div style={{ display: "flex", alignItems: "center", gap: 26, marginTop: 34 }}>
        {[0, 1, 2].map((i) => (
          <React.Fragment key={i}>
            <Ring size={62} p={pop(t, cue(sc, "Tiga") + i * 0.18)}>
              <span style={{ fontFamily: F.serif, fontSize: 28, color: C.gold }}>{i + 1}</span>
            </Ring>
            {i < 2 && <div style={{ width: 80 * draw(t, cue(sc, "Tiga") + i * 0.18 + 0.1, 0.4), height: 2, background: C.gold }} />}
          </React.Fragment>
        ))}
      </div>
      <In t={t} at={cue(sc, "hala")} style={{ marginTop: 28 }}>
        <div style={{ fontFamily: F.serif, fontStyle: "italic", fontWeight: 500, fontSize: 40, color: C.cream }}>Tiga fasa, satu hala tuju</div>
      </In>
    </div>
  );
};

export const RoadmapScene: React.FC<P> = ({ sc, t }) => {
  const nodes = sc.nodes as string[];
  const keys = Object.keys(sc.cueT);
  const outro = sc.kind === "outro";
  const final = outro ? cue(sc, "Inilah") : 99;
  const shrink = outro ? rise(t, final, 0.7) : 0;
  const X = [420, 960, 1500];
  const lineY = 520;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      {!outro && (
        <In t={t} at={0.3} style={{ position: "absolute", top: 210, left: 0, right: 0, textAlign: "center" }}>
          <Eyebrow>Hala Tuju 3 Fasa</Eyebrow>
        </In>
      )}
      <div style={{ position: "absolute", inset: 0, opacity: 1 - shrink, transform: `translateY(${-shrink * 60}px)` }}>
        <div style={{ position: "absolute", top: lineY - 1, left: X[0], width: (X[2] - X[0]) * draw(t, cue(sc, keys[0]) - 0.2, outro ? 3.0 : 6.2), height: 3, background: goldFill }} />
        {nodes.map((n, i) => {
          const at = cue(sc, keys[i]);
          const p = pop(t, at, 0.55);
          const lit = rise(t, at, 0.4);
          return (
            <div key={n} style={{ position: "absolute", left: X[i] - 200, top: lineY - 80, width: 400, display: "flex", flexDirection: "column", alignItems: "center" }}>
              <Ring size={160} p={p} filled={lit > 0.5 && outro}>
                <span style={{ fontFamily: F.serif, fontWeight: 700, fontSize: 76, ...(outro && lit > 0.5 ? { color: C.ink } : goldText) }}>{i + 1}</span>
              </Ring>
              <div style={{ marginTop: 34, opacity: lit, transform: `translateY(${(1 - lit) * 20}px)`, textAlign: "center" }}>
                {!outro && <div style={{ fontFamily: F.sans, fontSize: 22, letterSpacing: 7, color: C.gold }}>FASA {i + 1}</div>}
                <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: outro ? 46 : 52, color: C.cream, marginTop: 6, lineHeight: 1.15 }}>{n}</div>
              </div>
            </div>
          );
        })}
      </div>
      {outro && (
        <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: shrink }}>
          <div style={{ position: "relative", transform: `scale(${0.8 + 0.2 * pop(t, final, 0.7)})` }}>
            <Img src={staticFile("img/logo.png")} style={{ width: 230, height: 230, borderRadius: 115, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
            <Sheen t={t} at={final + 0.5} w={230} h={230} />
          </div>
          <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: 88, ...goldText, marginTop: 24 }}>Aimi Curtain</div>
          <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 26, letterSpacing: 12, color: C.cream, marginTop: 10 }}>PELAN PERTUMBUHAN</div>
        </div>
      )}
    </div>
  );
};

export const PhaseScene: React.FC<P> = ({ sc, t }) => {
  const n = sc.phase as number;
  const title = sc.title as string[];
  const num = rise(t, 0.25, 0.9);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      {/* big watermark ring */}
      <div style={{ position: "absolute", right: -160, top: 140, width: 900, height: 900, borderRadius: 450, border: `1.5px solid rgba(216,180,106,${0.18 * num})`, transform: `scale(${0.85 + 0.15 * num})` }} />
      <div style={{ position: "absolute", left: 150, top: 300, display: "flex", alignItems: "center", gap: 70 }}>
        <div style={{ position: "relative", overflow: "hidden", height: 380 }}>
          <div style={{ fontFamily: F.serif, fontWeight: 700, fontSize: 400, lineHeight: 0.95, ...goldText, transform: `translateY(${(1 - num) * 380}px)` }}>0{n}</div>
          <Sheen t={t} at={1.1} w={460} h={380} />
        </div>
        <div style={{ width: 2, height: 330 * draw(t, 0.5, 0.7), background: C.line }} />
        <div>
          <In t={t} at={0.6}><Eyebrow>Fasa {n} · Tema</Eyebrow></In>
          {title.map((l, i) => (
            <In key={i} t={t} at={cue(sc, Object.keys(sc.cueT)[0]) - 0.3 + i * 0.25} y={40}>
              <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: 96, color: C.cream, lineHeight: 1.12, marginTop: i ? 0 : 18 }}>{l}</div>
            </In>
          ))}
          <In t={t} at={cue(sc, "Fokusnya")} x={-30} y={0} style={{ marginTop: 34, display: "flex", alignItems: "center", gap: 22 }}>
            <div style={{ width: 70, height: 2, background: C.gold }} />
            <div style={{ fontFamily: F.serif, fontStyle: "italic", fontWeight: 500, fontSize: 42, color: C.cream }}>Fokus: {sc.focus as string}</div>
          </In>
        </div>
      </div>
    </div>
  );
};

export const ActionScene: React.FC<P> = ({ sc, t }) => {
  const p = pop(t, 0.2, 0.6);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", left: 140, top: 250, width: 700 }}>
        <In t={t} at={0.15}>
          <Eyebrow>Fasa {sc.phase as number} · Tindakan {sc.n as number}/{sc.of as number}</Eyebrow>
        </In>
        <div style={{ marginTop: 44 }}>
          <Ring size={150} p={p}><Icon name={sc.icon as string} size={84} /></Ring>
        </div>
        <In t={t} at={0.45} y={36} style={{ marginTop: 44 }}>
          <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: 70, color: C.cream, lineHeight: 1.12 }}>{sc.title as string}</div>
        </In>
        <In t={t} at={0.75} style={{ marginTop: 28, display: "flex", gap: 20, alignItems: "flex-start" }}>
          <div style={{ width: 4, alignSelf: "stretch", background: C.gold, borderRadius: 2 }} />
          <div style={{ fontFamily: F.sans, fontWeight: 400, fontSize: 32, color: C.muted, lineHeight: 1.45 }}>{sc.sub as string}</div>
        </In>
      </div>
      <div style={{ position: "absolute", left: 930, top: 170, width: 860, height: 760, borderRadius: 28, background: C.panel, border: `1.5px solid ${C.line}`, opacity: rise(t, 0.3), transform: `translateX(${(1 - rise(t, 0.3)) * 40}px)`, overflow: "hidden" }}>
        <Viz sc={sc} t={t} />
      </div>
    </div>
  );
};

export const GoalScene: React.FC<P> = ({ sc, t }) => {
  const kpiAt = cue(sc, "Tanda");
  const kpiKeys = Object.keys(sc.cueT).slice(Object.keys(sc.cueT).indexOf("Tanda") + 1);
  const sw = rise(t, kpiAt - 0.2, 0.6);
  const kpi = sc.kpi as string[];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <In t={t} at={0.3} x={-40} y={0} style={{ position: "absolute", left: 140, top: 250, width: 820 }}>
        <div style={{ borderLeft: `6px solid ${C.gold}`, background: "linear-gradient(90deg, rgba(216,180,106,0.12), rgba(216,180,106,0.03))", borderRadius: "0 18px 18px 0", padding: "50px 56px" }}>
          <Eyebrow>Matlamat Utama</Eyebrow>
          <div style={{ fontFamily: F.serif, fontWeight: 500, fontSize: 52, color: C.cream, lineHeight: 1.35, marginTop: 26 }}>{sc.goal as string}</div>
        </div>
      </In>
      <div style={{ position: "absolute", left: 1040, top: 190, width: 760, height: 720 }}>
        <div style={{ position: "absolute", inset: 0, opacity: 1 - sw, transform: `translateY(${-sw * 30}px)` }}>
          <GoalViz sc={sc} t={t} />
        </div>
        <div style={{ position: "absolute", inset: 0, opacity: sw, transform: `translateY(${(1 - sw) * 40}px)` }}>
          <div style={{ background: goldFill, borderRadius: 18, padding: "26px 36px", boxShadow: "0 18px 50px rgba(0,0,0,0.35)" }}>
            <div style={{ fontFamily: F.sans, fontWeight: 600, fontSize: 24, letterSpacing: 7, color: C.ink }}>PETUNJUK KEJAYAAN (KPI)</div>
          </div>
          <div style={{ marginTop: 34, display: "flex", flexDirection: "column", gap: 26 }}>
            {kpi.map((k, i) => {
              const at = cue(sc, kpiKeys[i]);
              const p = pop(t, at, 0.5);
              return (
                <div key={k} style={{ display: "flex", alignItems: "center", gap: 26, opacity: Math.min(1, 0.25 + p), transform: `translateX(${(1 - p) * 30}px)` }}>
                  <Ring size={76} p={0.85 + 0.15 * p} filled={p > 0.6}>
                    <Icon name="check" size={44} color={p > 0.6 ? C.ink : C.gold} sw={4} />
                  </Ring>
                  <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 36, color: C.cream, lineHeight: 1.3 }}>{k}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
