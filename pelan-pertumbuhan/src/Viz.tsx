import React from "react";
import { Easing, Img, interpolate, staticFile } from "remotion";
import { C, F, goldFill, goldText } from "./theme";
import { Chip, clamp, draw, Icon, pop, rise, Ring, Scene } from "./ui";

type P = { sc: Scene; t: number };
const W = 860;
const H = 760;
const abs = (x: number, y: number, extra: React.CSSProperties = {}): React.CSSProperties => ({ position: "absolute", left: x, top: y, ...extra });
const Label: React.FC<{ children: React.ReactNode; size?: number; color?: string; style?: React.CSSProperties }> = ({ children, size = 30, color = C.cream, style }) => (
  <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: size, color, textAlign: "center", lineHeight: 1.25, ...style }}>{children}</div>
);

// ---------------------------------------------------------------- Fasa 1
const Usp: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const steps: [string, string, number][] = [["Ukur", "ruler", c.Ukur], ["Jahit", "scissors", c.jahit], ["Pasang", "hook", c.pasang]];
  const badge = pop(t, c.USP, 0.6);
  return (
    <>
      <div style={abs(0, 70, { width: W, display: "flex", justifyContent: "center" })}>
        <div style={{ transform: `scale(${badge})`, opacity: Math.min(1, badge * 1.5), textAlign: "center" }}>
          <div style={{ fontFamily: F.sans, fontSize: 22, letterSpacing: 8, color: C.gold }}>USP SYARIKAT</div>
          <div style={{ fontFamily: F.serif, fontWeight: 700, fontSize: 150, lineHeight: 1.05, ...goldText }}>
            A<span style={{ fontSize: 110, margin: "0 18px", opacity: draw(t, c.A, 0.5) }}>→</span>
            <span style={{ opacity: rise(t, c.A + 0.2, 0.4) }}>Z</span>
          </div>
          <Label size={30} color={C.muted}>Langsir tempahan khas, siap sepenuhnya</Label>
        </div>
      </div>
      <div style={abs(130, 520, { width: 600, height: 2, background: C.line })}>
        <div style={{ width: `${draw(t, c.Ukur, c.pasang - c.Ukur + 0.3) * 100}%`, height: 2, background: C.gold }} />
      </div>
      {steps.map(([l, ic, at], i) => {
        const p = pop(t, at, 0.4);
        return (
          <div key={l} style={abs(70 + i * 260, 440, { width: 200, display: "flex", flexDirection: "column", alignItems: "center" })}>
            <Ring size={160} p={0.6 + 0.4 * p} filled={p > 0.5}><Icon name={ic} size={84} color={p > 0.5 ? C.ink : C.gold} /></Ring>
            <Label size={38} style={{ marginTop: 20, opacity: 0.3 + 0.7 * p }}>{l}</Label>
          </div>
        );
      })}
    </>
  );
};

const Sop: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const roles: [string, string, number][] = [["Layan WhatsApp", "chat", c.WhatsApp], ["Potong & Jahit", "scissors", c.memotong], ["Pasang", "hook", c.memasang]];
  const doc = pop(t, c.SOP, 0.5);
  return (
    <>
      <div style={abs(0, 50, { width: W, display: "flex", justifyContent: "center", alignItems: "center", gap: 20 })}>
        <div style={{ transform: `scale(${doc}) rotate(${(1 - doc) * -10}deg)`, opacity: Math.min(1, doc * 1.5), display: "flex", alignItems: "center", gap: 18, background: goldFill, padding: "16px 34px", borderRadius: 16 }}>
          <Icon name="doc" size={52} color={C.ink} sw={3} />
          <div style={{ fontFamily: F.sans, fontWeight: 600, fontSize: 40, color: C.ink, letterSpacing: 3 }}>SOP KERJA</div>
        </div>
      </div>
      {roles.map(([l, ic, at], i) => {
        const p = pop(t, at, 0.45);
        const x = 40 + i * 270;
        return (
          <div key={l} style={abs(x, 190, { width: 240, height: 360, borderRadius: 22, border: `1.5px solid ${p > 0.5 ? C.gold : C.line}`, background: "rgba(243,234,214,0.04)", display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 30, opacity: 0.25 + 0.75 * p, transform: `translateY(${(1 - p) * 40}px)` })}>
            <Ring size={96} p={1}><Icon name="user" size={56} /></Ring>
            <div style={{ marginTop: 18, fontFamily: F.sans, fontSize: 20, letterSpacing: 4, color: C.gold }}>STAF {i + 1}</div>
            <div style={{ marginTop: 22 }}><Icon name={ic} size={62} color={C.cream} /></div>
            <Label size={28} style={{ marginTop: 14, padding: "0 12px" }}>{l}</Label>
          </div>
        );
      })}
      <div style={abs(0, 600, { width: W, display: "flex", justifyContent: "center", gap: 22 })}>
        <Chip p={pop(t, c.bertindih)}>✓ Tak bertindih</Chip>
        <Chip p={pop(t, c.burnout)} gold>✓ Elak burnout</Chip>
      </div>
    </>
  );
};

const Capacity: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const bars = [0.35, 0.45, 0.55, 0.62, 0.74, 0.86, 0.97];
  const base = 560;
  const maxH = 380;
  const capY = base - maxH * 0.95;
  const grow = (i: number) => rise(t, c.leads + i * 0.22, 0.5);
  const inst = pop(t, c.installer, 0.55);
  return (
    <>
      <Label size={24} color={C.gold} style={abs(60, 60, { textAlign: "left", letterSpacing: 6 })}>LEADS MINGGUAN</Label>
      <div style={abs(60, capY, { width: 560, borderTop: `3px dashed ${C.goldLight}`, opacity: rise(t, c.kapasiti) })} />
      <Label size={24} color={C.goldLight} style={abs(60, capY - 44, { textAlign: "left", opacity: rise(t, c.kapasiti) })}>Kapasiti maksimum</Label>
      {bars.map((b, i) => (
        <div key={i} style={abs(70 + i * 76, base - maxH * b * grow(i), { width: 52, height: maxH * b * grow(i), borderRadius: "8px 8px 0 0", background: i >= 5 ? goldFill : "rgba(216,180,106,0.45)" })} />
      ))}
      <div style={abs(60, base, { width: 560, height: 2, background: C.line })} />
      <div style={abs(640, 200, { width: 200, display: "flex", flexDirection: "column", alignItems: "center", transform: `scale(${inst})`, opacity: Math.min(1, inst * 1.5) })}>
        <Ring size={150} p={1} filled><Icon name="user" size={80} color={C.ink} sw={3} /></Ring>
        <div style={{ marginTop: 12, fontFamily: F.serif, fontWeight: 700, fontSize: 56, ...goldText }}>+1</div>
        <Label size={30}>Installer</Label>
      </div>
      <div style={abs(0, 630, { width: W, display: "flex", justifyContent: "center" })}>
        <Chip p={pop(t, c.kritikal)}>Bahagian kritikal sahaja</Chip>
      </div>
    </>
  );
};

// ---------------------------------------------------------------- Fasa 2
const Geo: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const houses = [[250, 360], [330, 300], [420, 370], [510, 310], [600, 380], [330, 450], [470, 460], [560, 470]];
  const ring = (k: number) => {
    const ph = ((t - c.geo) / 1.6 + k / 3) % 1;
    return t < c.geo ? 0 : ph;
  };
  const budget = rise(t, c.bajet, 0.8);
  return (
    <>
      {[0, 1, 2].map((k) => (
        <div key={k} style={abs(430 - 260 * ring(k), 390 - 260 * ring(k), { width: 520 * ring(k), height: 520 * ring(k), borderRadius: 999, border: `2px solid ${C.gold}`, opacity: (1 - ring(k)) * 0.8 })} />
      ))}
      {houses.map(([x, y], i) => {
        const p = pop(t, c.taman + i * 0.08, 0.4);
        return (
          <div key={i} style={abs(x - 34, y - 34, { transform: `scale(${p})`, opacity: Math.min(1, p * 1.5) })}>
            <Icon name="house" size={68} color={C.cream} />
          </div>
        );
      })}
      <div style={abs(398, 358, { opacity: rise(t, c.geo) })}>
        <Icon name="target" size={64} />
      </div>
      <div style={abs(40, 60, { display: "flex", alignItems: "center", gap: 16 })}>
        <div style={{ width: 22, height: 120, borderRadius: 6, background: "rgba(243,234,214,0.1)", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", bottom: 0, width: "100%", height: `${30 + 70 * budget}%`, background: goldFill }} />
        </div>
        <div>
          <Label size={22} color={C.gold} style={{ textAlign: "left", letterSpacing: 5 }}>BAJET MARKETING</Label>
          <div style={{ display: "flex", alignItems: "center", gap: 6, opacity: budget }}><Icon name="up" size={40} sw={3.5} /><Label size={34} style={{ textAlign: "left" }}>Ditingkatkan</Label></div>
        </div>
      </div>
      <div style={abs(0, 600, { width: W, display: "flex", justifyContent: "center", gap: 18 })}>
        <Chip p={pop(t, c.taman)}>Taman perumahan baharu</Chip>
        <Chip p={pop(t, c.serah)} gold><Icon name="key" size={34} color={C.ink} sw={3} /> Serah kunci</Chip>
      </div>
    </>
  );
};

const Billboard: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const up = rise(t, c.persimpangan - 0.3, 0.8);
  return (
    <>
      {/* crossroads */}
      <div style={abs(0, 560, { width: W, height: 70, background: "rgba(243,234,214,0.08)", opacity: draw(t, 0.4) })} />
      <div style={abs(560, 300, { width: 70, height: 460, background: "rgba(243,234,214,0.08)", opacity: draw(t, 0.6) })} />
      <div style={abs(0, 593, { width: W * draw(t, 0.4), borderTop: `3px dashed rgba(243,234,214,0.35)` })} />
      {/* billboard */}
      <div style={abs(80, 560 - 470 * up, { width: 440, opacity: Math.min(1, up * 2) })}>
        <div style={{ height: 230, borderRadius: 12, background: `linear-gradient(140deg, #24463C, #142C26)`, border: `5px solid ${C.gold}`, display: "flex", alignItems: "center", justifyContent: "center", gap: 18, boxShadow: "0 20px 50px rgba(0,0,0,0.4)" }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 110, height: 110, borderRadius: 55, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
          <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: 46, ...goldText, lineHeight: 1.05 }}>Aimi<br />Curtain</div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-around", padding: "0 90px" }}>
          <div style={{ width: 14, height: 240, background: C.goldDark }} />
          <div style={{ width: 14, height: 240, background: C.goldDark }} />
        </div>
      </div>
      <Label size={24} color={C.gold} style={abs(570, 650, { letterSpacing: 4, width: 270, textAlign: "left" })}>KULIM</Label>
      <div style={abs(560, 120, { display: "flex", flexDirection: "column", gap: 22 })}>
        {([["Kredibiliti", c.kredibiliti], ["Kepercayaan", c.kepercayaan]] as [string, number][]).map(([l, at]) => (
          <div key={l} style={{ display: "flex", alignItems: "center", gap: 8, opacity: rise(t, at), transform: `translateY(${(1 - rise(t, at)) * 20}px)` }}>
            <Icon name="up" size={44} sw={3.5} />
            <Label size={34} style={{ textAlign: "left" }}>{l}</Label>
          </div>
        ))}
      </div>
    </>
  );
};

const Testimonials: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const cards: [string, number, number, number, number, boolean][] = [
    ["img/foto1.jpg", c.gambar, 90, 110, -8, false],
    ["img/foto2.jpg", c.gambar + 0.35, 320, 90, 4, false],
    ["img/video1.jpg", c.video, 550, 130, 9, true],
  ];
  const flash = interpolate(t, [c.gambar - 0.05, c.gambar + 0.05, c.gambar + 0.4], [0, 0.6, 0], clamp);
  return (
    <>
      {cards.map(([src, at, x, y, r, vid], i) => {
        const p = pop(t, at, 0.55);
        return (
          <div key={i} style={abs(x, y, { width: 220, padding: 12, paddingBottom: 46, background: "#F6F0E4", borderRadius: 6, boxShadow: "0 18px 40px rgba(0,0,0,0.45)", transform: `translateY(${(1 - p) * 120}px) rotate(${r * p}deg) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 1.5) })}>
            <div style={{ position: "relative", width: 196, height: 300, overflow: "hidden" }}>
              <Img src={staticFile(src)} style={{ width: 196, height: 300, objectFit: "cover" }} />
              {vid && (
                <div style={{ position: "absolute", left: 63, top: 115, width: 70, height: 70, borderRadius: 35, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon name="play" size={44} color="#fff" sw={3} />
                </div>
              )}
            </div>
            <div style={{ position: "absolute", bottom: 10, left: 0, right: 0, textAlign: "center", fontFamily: F.sans, fontSize: 20, color: "#5A5A50" }}>{vid ? "Video" : "Gambar"}</div>
          </div>
        );
      })}
      <div style={abs(0, 0, { width: W, height: H, background: "#fff", opacity: flash })} />
      <div style={abs(0, 580, { width: W, display: "flex", justifyContent: "center" })}>
        <Chip p={pop(t, c.before)} gold style={{ fontSize: 34 }}>Kempen Before & After premium</Chip>
      </div>
      <Label size={20} color={C.muted} style={abs(0, 680, { width: W, opacity: rise(t, c.gambar) })}>Contoh: kerja pemasangan Aimi Curtain</Label>
    </>
  );
};

const Store: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const g = interpolate(t, [c.ground - 0.4, c.ground + 0.5], [0.55, 1], { easing: Easing.out(Easing.back(1.2)), ...clamp });
  const tags: [string, number][] = [["Ground floor", c.ground], ["Display langsir saiz sebenar", c.display], ["Mockup ruang tamu", c.mockup]];
  return (
    <>
      <div style={abs(205, 50, { width: 450, height: 380, transform: `scale(${g})`, transformOrigin: "50% 100%" })}>
        <div style={{ height: 70, background: goldFill, borderRadius: "10px 10px 0 0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: F.serif, fontWeight: 600, fontSize: 38, color: C.ink }}>Aimi Curtain</div>
        <div style={{ height: 22, background: `repeating-linear-gradient(90deg, ${C.gold} 0 40px, ${C.cream} 40px 80px)` }} />
        <div style={{ height: 250, border: `3px solid ${C.gold}`, borderTop: "none", display: "flex", gap: 14, padding: 20, background: "rgba(10,30,25,0.6)" }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ flex: 1, background: i === 1 ? "rgba(243,234,214,0.08)" : "rgba(243,234,214,0.04)", border: `1.5px solid ${C.line}`, display: "flex", alignItems: "flex-end", justifyContent: "center", overflow: "hidden", position: "relative" }}>
              {i !== 1 && (
                <div style={{ position: "absolute", top: 8, bottom: 0, left: 8, right: 8, background: `repeating-linear-gradient(90deg, rgba(216,180,106,0.55) 0 10px, rgba(216,180,106,0.25) 10px 20px)`, opacity: rise(t, c.display), transform: `scaleY(${rise(t, c.display)})`, transformOrigin: "50% 0%" }} />
              )}
              {i === 1 && <div style={{ marginBottom: 20, opacity: rise(t, c.mockup) }}><Icon name="store" size={64} color={C.cream} /></div>}
            </div>
          ))}
        </div>
      </div>
      <div style={abs(40, 500, { width: W - 80, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 16 })}>
        {tags.map(([l, at]) => <Chip key={l} p={pop(t, at)}>{l}</Chip>)}
      </div>
      <div style={abs(620, 70, { opacity: rise(t, c.eksklusif) })}><Icon name="star" size={64} /></div>
    </>
  );
};

// ---------------------------------------------------------------- Fasa 3
const Developer: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const join = draw(t, c.pemaju, 0.7);
  const v = rise(t, c.welcome, 0.8);
  return (
    <>
      <div style={abs(60, 70, { display: "flex", alignItems: "center" })}>
        <div style={{ width: 280, display: "flex", flexDirection: "column", alignItems: "center", opacity: rise(t, c.pemaju - 0.3) }}>
          <Ring size={120}><Icon name="building" size={66} /></Ring>
          <Label size={28} style={{ marginTop: 12 }}>Pemaju hartanah</Label>
        </div>
        <div style={{ width: 180, height: 3, background: goldFill, transform: `scaleX(${join})`, position: "relative", top: -26 }}>
          <div style={{ position: "absolute", left: 60, top: -32, opacity: join }}><Icon name="handshake" size={64} color={C.goldLight} /></div>
        </div>
        <div style={{ width: 280, display: "flex", flexDirection: "column", alignItems: "center", opacity: rise(t, c.pemaju) }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 120, height: 120, borderRadius: 60, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
          <Label size={28} style={{ marginTop: 12 }}>Aimi Curtain</Label>
        </div>
      </div>
      {/* showhouse */}
      <div style={abs(60, 330, { width: 340, height: 330, borderRadius: 22, border: `1.5px solid ${C.line}`, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 30, opacity: rise(t, c.showhouse), transform: `translateY(${(1 - rise(t, c.showhouse)) * 30}px)` })}>
        <Icon name="house" size={110} color={C.cream} />
        <Label size={32} style={{ marginTop: 10 }}>Showhouse</Label>
        <Label size={24} color={C.muted} style={{ marginTop: 6 }}>Langsir tajaan / diskaun</Label>
      </div>
      {/* welcome kit + voucher */}
      <div style={abs(460, 330, { width: 340, height: 330, borderRadius: 22, border: `1.5px solid ${C.line}`, display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 30, opacity: rise(t, c.baucar) })}>
        <div style={{ position: "relative", height: 130, width: 200 }}>
          <div style={{ position: "absolute", left: 40, top: 40 }}><Icon name="gift" size={110} color={C.cream} /></div>
          <div style={{ position: "absolute", left: 30, top: 130 - 200 * (1 - v) - 70 * v, transform: `rotate(${-10 + 10 * v}deg)`, opacity: 1 - v * 0.2 }}>
            <div style={{ width: 150, height: 70, borderRadius: 10, background: goldFill, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: F.sans, fontWeight: 600, fontSize: 20, color: C.ink }}>BAUCAR</div>
          </div>
        </div>
        <Label size={32} style={{ marginTop: 10 }}>Welcome kit</Label>
        <Label size={24} color={C.muted} style={{ marginTop: 6 }}>Baucar untuk pembeli rumah</Label>
      </div>
    </>
  );
};

const Commercial: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const tiles: [string, string, number][] = [["Hotel butik", "bed", c.hotel], ["Homestay premium", "house", c.homestay], ["Pejabat pengurusan", "office", c.pejabat]];
  return (
    <>
      <div style={abs(0, 80, { width: W, display: "flex", justifyContent: "center", gap: 18 })}>
        <Chip p={pop(t, c.blackout)}>Langsir blackout</Chip>
        <Chip p={pop(t, c.bidai)}>Bidai</Chip>
        <Chip p={pop(t, c.pukal)} gold>Pakej pukal</Chip>
      </div>
      {tiles.map(([l, ic, at], i) => {
        const p = pop(t, at, 0.45);
        return (
          <div key={l} style={abs(40 + i * 270, 250, { width: 240, height: 330, borderRadius: 22, border: `1.5px solid ${p > 0.5 ? C.gold : C.line}`, background: "rgba(243,234,214,0.04)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 22, opacity: 0.2 + 0.8 * p, transform: `translateY(${(1 - p) * 40}px)` })}>
            <Ring size={130}><Icon name={ic} size={72} /></Ring>
            <Label size={30} style={{ padding: "0 14px" }}>{l}</Label>
          </div>
        );
      })}
      <Label size={24} color={C.muted} style={abs(0, 640, { width: W, opacity: rise(t, c.hotel) })}>Sasaran jualan pukal</Label>
    </>
  );
};

const Vendor: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const lines = [0, 1, 2, 3, 4];
  const items: [string, number][] = [["Layak masuk tender", c.tender], ["Sebut harga projek", c.sebut]];
  return (
    <>
      <div style={abs(70, 90, { width: 320, height: 430, background: "#F6F0E4", borderRadius: 10, padding: 30, boxShadow: "0 20px 50px rgba(0,0,0,0.4)", opacity: rise(t, c.profil - 0.3), transform: `rotate(-3deg) translateY(${(1 - rise(t, c.profil - 0.3)) * 40}px)` })}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Img src={staticFile("img/logo.png")} style={{ width: 70, height: 70, borderRadius: 35, WebkitMaskImage: "radial-gradient(circle, #000 58%, transparent 71%)" }} />
          <div style={{ fontFamily: F.serif, fontWeight: 600, fontSize: 26, color: C.ink, lineHeight: 1.1 }}>Profil<br />Syarikat</div>
        </div>
        <div style={{ marginTop: 26, display: "flex", flexDirection: "column", gap: 18 }}>
          {lines.map((i) => (
            <div key={i} style={{ height: 14, borderRadius: 7, background: i === 0 ? C.gold : "#D8D0BF", width: `${(i === 0 ? 70 : 100 - i * 9) * draw(t, c.profil + i * 0.15, 0.4)}%` }} />
          ))}
        </div>
        <div style={{ marginTop: 30, height: 90, borderRadius: 8, background: "#E9E1CF", opacity: draw(t, c.profil + 0.8, 0.4) }} />
      </div>
      <div style={abs(450, 150, { display: "flex", flexDirection: "column", gap: 34 })}>
        {items.map(([l, at]) => {
          const p = pop(t, at, 0.45);
          return (
            <div key={l} style={{ display: "flex", alignItems: "center", gap: 18, opacity: 0.25 + 0.75 * p }}>
              <Ring size={74} p={0.85 + 0.15 * p} filled={p > 0.5}><Icon name="check" size={42} color={p > 0.5 ? C.ink : C.gold} sw={4} /></Ring>
              <Label size={32} style={{ textAlign: "left", width: 260 }}>{l}</Label>
            </div>
          );
        })}
      </div>
      <div style={abs(0, 600, { width: W, display: "flex", justifyContent: "center", gap: 18 })}>
        <Chip p={pop(t, c.institusi)}>Institusi</Chip>
        <Chip p={pop(t, c.institusi + 0.5)}>Syarikat swasta</Chip>
      </div>
    </>
  );
};

const MAP: Record<string, React.FC<P>> = { usp: Usp, sop: Sop, capacity: Capacity, geo: Geo, billboard: Billboard, testimonials: Testimonials, store: Store, developer: Developer, commercial: Commercial, vendor: Vendor };

export const Viz: React.FC<P> = ({ sc, t }) => {
  const V = MAP[sc.viz as string];
  return V ? <V sc={sc} t={t} /> : null;
};

// ---------------------------------------------------------------- goal visuals (right side, before KPI)
const Flow: React.FC<P> = ({ t }) => {
  const tickets = [0, 1, 2, 3, 4, 5];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Label size={24} color={C.gold} style={abs(0, 70, { width: 760, letterSpacing: 6 })}>TEMPAHAN MASUK BERTERUSAN</Label>
      <div style={abs(40, 360, { width: 480, height: 3, background: C.line })} />
      {tickets.map((i) => {
        const ph = ((t * 0.32 + i / tickets.length) % 1);
        return (
          <div key={i} style={abs(20 + ph * 470, 318, { opacity: Math.sin(Math.PI * ph) * rise(t, 0.8) })}>
            <Icon name="ticket" size={80} color={C.cream} />
          </div>
        );
      })}
      <div style={abs(520, 230, { transform: `rotate(${t * 40}deg)`, opacity: rise(t, 0.6) })}><Icon name="gear" size={250} /></div>
      <div style={abs(560, 520, { display: "flex", alignItems: "center", gap: 10, opacity: rise(t, 1.6) })}>
        <Icon name="check" size={44} sw={4} />
        <Label size={30} style={{ textAlign: "left", whiteSpace: "nowrap" }}>Kualiti terjaga</Label>
      </div>
    </div>
  );
};

const MapViz: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  // schematic positions (not to scale)
  const pins: [string, number, number, number][] = [["Bukit Mertajam", 150, 230, c.Bukit], ["Kulim", 520, 210, c.Kulim], ["Lunas", 360, 430, c.Lunas]];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={abs(40, 90, { width: 680, height: 520, borderRadius: 30, border: `1.5px solid ${C.line}`, background: "repeating-linear-gradient(45deg, rgba(243,234,214,0.025) 0 18px, rgba(0,0,0,0) 18px 36px)", opacity: rise(t, 0.6) })} />
      <svg width={760} height={720} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d="M150 270 Q 330 300 520 250 M 520 250 Q 470 400 360 470 M 360 470 Q 230 400 150 270" fill="none" stroke={C.gold} strokeWidth={2} strokeDasharray="8 8" opacity={draw(t, c.Bukit + 0.3, 0.8) * 0.7} />
      </svg>
      {pins.map(([l, x, y, at]) => {
        const p = pop(t, at, 0.5);
        return (
          <div key={l} style={abs(x - 40, y - 70, { display: "flex", flexDirection: "column", alignItems: "center", transform: `translateY(${(1 - p) * -40}px)`, opacity: Math.min(1, p * 1.5), width: 80 })}>
            <Icon name="pin" size={80} color={C.goldLight} sw={3} />
            <div style={{ fontFamily: F.sans, fontWeight: 500, fontSize: 28, color: C.cream, whiteSpace: "nowrap", marginTop: 4 }}>{l}</div>
          </div>
        );
      })}
      <div style={abs(0, 640, { width: 760, display: "flex", justifyContent: "center" })}>
        <Chip p={pop(t, 1.6)} gold>No. 1 · Top of Mind</Chip>
      </div>
    </div>
  );
};

const Stable: React.FC<P> = ({ sc, t }) => {
  const c = sc.cueT;
  const jag = "M40 420 L120 360 L180 450 L250 330 L320 470 L400 350 L470 460 L540 340 L620 440 L700 380";
  const smooth = "M40 470 C 200 440, 360 400, 520 360 S 680 320, 720 300";
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Label size={24} color={C.gold} style={abs(0, 70, { width: 760, letterSpacing: 6 })}>PENDAPATAN (ILUSTRASI)</Label>
      <svg width={760} height={620} style={{ position: "absolute", left: 0, top: 60 }}>
        <path d={jag} fill="none" stroke="rgba(243,234,214,0.35)" strokeWidth={4} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw(t, 0.6, 1.2)} />
        <path d={smooth} fill="none" stroke={C.goldLight} strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw(t, c.kestabilan - 0.2, 1.2)} />
        <line x1={40} y1={540} x2={720} y2={540} stroke={C.line} strokeWidth={2} />
      </svg>
      <div style={abs(60, 600, { display: "flex", gap: 30 })}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, opacity: rise(t, 0.8) }}><div style={{ width: 40, height: 4, background: "rgba(243,234,214,0.45)" }} /><Label size={24} color={C.muted}>Runcit sahaja</Label></div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, opacity: rise(t, c.kestabilan) }}><div style={{ width: 40, height: 6, background: C.goldLight }} /><Label size={24}>+ Kontrak pukal B2B</Label></div>
      </div>
    </div>
  );
};

const GMAP: Record<string, React.FC<P>> = { flow: Flow, map: MapViz, stable: Stable };
export const GoalViz: React.FC<P> = ({ sc, t }) => {
  const V = GMAP[sc.goalViz as string];
  return V ? <V sc={sc} t={t} /> : null;
};
