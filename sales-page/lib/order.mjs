// Nombor order + token bertandatangan supaya resit yang dimuat naik boleh dipadankan dengan order sebenar.
import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";

const key = () => process.env.ORDER_SECRET || process.env.TELEGRAM_BOT_TOKEN || process.env.BILLPLZ_X_SIGNATURE || "jbh";
const CHARS = "ACDEFGHJKMNPQRTUVWXY34679";

export function newOrderId(now = new Date()) {
  const my = new Date(now.getTime() + 8 * 3600e3); // waktu Malaysia
  const d = my.toISOString().slice(2, 10).replace(/-/g, "");
  const r = [...randomBytes(4)].map(b => CHARS[b % CHARS.length]).join("");
  return `JBH-${d}-${r}`;
}
// data = { id, jumlah, nama, tel, bayar }
export function signOrder(o) {
  const payload = Buffer.from(JSON.stringify(o)).toString("base64url");
  const sig = createHmac("sha256", key()).update(payload).digest("base64url");
  return payload + "." + sig;
}
export function readOrder(token) {
  const [payload, sig] = String(token || "").split(".");
  if (!payload || !sig) return null;
  const want = createHmac("sha256", key()).update(payload).digest("base64url");
  const a = Buffer.from(want), b = Buffer.from(sig);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  try { return JSON.parse(Buffer.from(payload, "base64url").toString()); } catch (_) { return null; }
}
