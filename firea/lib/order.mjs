// Harga & postage Firea (mesti sama dengan CONFIG dalam firea.html dan shop.html).
export const PACKAGES = { 1: 35, 2: 55, 3: 69 };
export const EAST_SHIPPING = 15; // Sabah, Sarawak, Labuan. Semenanjung percuma.
export const STATES = ["Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", "Perak", "Perlis", "Pulau Pinang", "Selangor", "Terengganu", "WP Kuala Lumpur", "WP Putrajaya", "Sabah", "Sarawak", "WP Labuan"];
export const isEast = negeri => /Sabah|Sarawak|Labuan/.test(negeri);

// Voucher pembelian kedua (dicetak pada flyer dalam parcel, untuk order di website). Diskaun ikut pakej.
export const VOUCHER = "FIREAMUSK";
export const DISKAUN = { 1: 5, 2: 10, 3: 10 };
export const kodSah = kod => String(kod || "").trim().toUpperCase().replace(/\s+/g, "") === VOUCHER;

export function quote(qty, negeri, kod) {
  const price = PACKAGES[qty];
  if (!price || !STATES.includes(negeri)) return null;
  const pos = isEast(negeri) ? EAST_SHIPPING : 0;
  const diskaun = kodSah(kod) ? DISKAUN[qty] || 0 : 0;
  return { qty, price, pos, diskaun, voucher: diskaun ? VOUCHER : "", jumlah: price - diskaun + pos };
}
const SUMBER = { shop: "fireadeodorant.com/shop", repeat: "fireadeodorant.com/repeat" };
export const sumberLabel = s => SUMBER[s] || "fireadeodorant.com";
export const sumberKey = s => (s in SUMBER ? s : "website");

export function normMobile(t) {
  let d = String(t || "").replace(/\D/g, "");
  if (d.startsWith("0")) d = "6" + d;
  else if (d && !d.startsWith("6")) d = "60" + d;
  return d;
}

// Nombor order + token bertandatangan supaya resit yang dimuat naik boleh dipadankan dengan order sebenar.
import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
const key = () => process.env.ORDER_SECRET || process.env.TELEGRAM_BOT_TOKEN || "firea";
const CHARS = "ACDEFGHJKMNPQRTUVWXY34679";

export function newOrderId(now = new Date()) {
  const my = new Date(now.getTime() + 8 * 3600e3); // waktu Malaysia
  const d = my.toISOString().slice(2, 10).replace(/-/g, "");
  const r = [...randomBytes(4)].map(b => CHARS[b % CHARS.length]).join("");
  return `FIR-${d}-${r}`;
}
export function signOrder(o) {
  const payload = Buffer.from(JSON.stringify(o)).toString("base64url");
  return payload + "." + createHmac("sha256", key()).update(payload).digest("base64url");
}
export function readOrder(token) {
  const [payload, sig] = String(token || "").split(".");
  if (!payload || !sig) return null;
  const want = Buffer.from(createHmac("sha256", key()).update(payload).digest("base64url")), got = Buffer.from(sig);
  if (want.length !== got.length || !timingSafeEqual(want, got)) return null;
  try { return JSON.parse(Buffer.from(payload, "base64url").toString()); } catch (_) { return null; }
}
