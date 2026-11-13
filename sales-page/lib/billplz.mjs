// Pembantu Billplz: harga pakej (sumber sebenar di server), panggilan API dan semakan X Signature.
import { createHmac, timingSafeEqual } from "node:crypto";

export const PAKEJ = {
  1: { nama: "Pakej Cuba - 1 Botol", harga: 30, pos: 8 },
  2: { nama: "Pakej Usaha - 2 Botol", harga: 58, pos: 0 },
  3: { nama: "Pakej Bebas - 3 Botol", harga: 69, pos: 0 },
};
export const EAST = ["Sabah", "Sarawak", "W.P. Labuan"];
export const POS_EAST = 18;
export const STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", "Perak", "Perlis", "Pulau Pinang",
  "Selangor", "Terengganu", "W.P. Kuala Lumpur", "W.P. Putrajaya", "Sabah", "Sarawak", "W.P. Labuan"];

export function quote(pkg, negeri) {
  const p = PAKEJ[pkg];
  if (!p) return null;
  const pos = EAST.includes(negeri) ? POS_EAST : p.pos;
  return { ...p, posRM: pos, jumlah: p.harga + pos };
}

export function settings() {
  const sandbox = String(process.env.BILLPLZ_SANDBOX || "").toLowerCase() === "true";
  return {
    apiKey: process.env.BILLPLZ_API_KEY || "",
    collectionId: process.env.BILLPLZ_COLLECTION_ID || "",
    xKey: process.env.BILLPLZ_X_SIGNATURE || "",
    base: sandbox ? "https://www.billplz-sandbox.com/api/v3" : "https://www.billplz.com/api/v3",
    sandbox,
  };
}

// 012-345 6789 -> 60123456789
export function normMobile(t) {
  let d = String(t || "").replace(/\D/g, "");
  if (d.startsWith("0")) d = "6" + d;
  else if (d && !d.startsWith("6")) d = "60" + d;
  return d;
}

// Billplz X Signature: pasangan kunci+nilai (tanpa x_signature), disusun tanpa ikut huruf besar/kecil, dicantum dengan "|",
// kemudian HMAC-SHA256 (hex) dengan kunci X Signature. Kunci bersarang billplz[id] menjadi "billplzid".
export function sourceString(params) {
  const parts = [];
  for (const [k, v] of params) {
    const key = k.replace(/\[([^\]]*)\]/g, "$1");
    if (key === "x_signature" || key === "billplzx_signature") continue;
    parts.push(key + (v ?? ""));
  }
  return parts.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())).join("|");
}
export function sign(params, xKey) {
  return createHmac("sha256", xKey).update(sourceString(params)).digest("hex");
}
export function verify(params, xKey) {
  const given = (params.find(([k]) => k === "x_signature" || k === "billplz[x_signature]") || [])[1] || "";
  if (!xKey || !given) return false;
  const want = sign(params, xKey);
  const a = Buffer.from(want), b = Buffer.from(String(given));
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function billplz(path, { method = "GET", body } = {}) {
  const c = settings();
  const res = await fetch(c.base + path, {
    method,
    headers: {
      Authorization: "Basic " + Buffer.from(c.apiKey + ":").toString("base64"),
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = JSON.parse(text); } catch (_) { data = { raw: text }; }
  return { ok: res.ok, status: res.status, data };
}

export const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
