// Pembantu Billplz: tetapan dari Netlify, panggilan API dan semakan X Signature.
import { createHmac, timingSafeEqual } from "node:crypto";

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
export const ready = () => { const c = settings(); return Boolean(c.apiKey && c.collectionId && c.xKey); };

// X Signature: pasangan kunci+nilai (tanpa x_signature), disusun tanpa ikut huruf besar/kecil, dicantum "|",
// kemudian HMAC-SHA256 (hex). Kunci bersarang billplz[id] menjadi "billplzid".
export function sourceString(params) {
  const parts = [];
  for (const [k, v] of params) {
    const key = k.replace(/\[([^\]]*)\]/g, "$1");
    if (key === "x_signature" || key === "billplzx_signature") continue;
    parts.push(key + (v ?? ""));
  }
  return parts.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())).join("|");
}
export const sign = (params, xKey) => createHmac("sha256", xKey).update(sourceString(params)).digest("hex");
export function verify(params, xKey) {
  const given = (params.find(([k]) => k === "x_signature" || k === "billplz[x_signature]") || [])[1] || "";
  if (!xKey || !given) return false;
  const a = Buffer.from(sign(params, xKey)), b = Buffer.from(String(given));
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

// Penerangan bil menyimpan bilangan botol dan ID order supaya callback boleh bina notifikasi.
export const describe = (qty, id, sumber, q = {}) =>
  `Firea Celeste Musk (${qty} botol) · ${id} · ${sumber}` + (q.diskaun ? ` · voucher ${q.voucher} -RM${q.diskaun}` : "");
export function parseDesc(d) {
  const m = String(d || "").match(/\((\d) botol\) · (FIR-[A-Z0-9-]+)(?: · ([a-z]+))?/);
  const v = String(d || "").match(/voucher (\S+) -RM(\d+)/);
  return { qty: m ? Number(m[1]) : 0, id: m ? m[2] : "", sumber: m && m[3] || "", voucher: v ? v[1] : "", diskaun: v ? Number(v[2]) : 0 };
}
