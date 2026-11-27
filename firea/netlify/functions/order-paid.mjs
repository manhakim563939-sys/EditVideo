// POST /api/order-paid  { token, pembayar? }
// Pelanggan DuitNow tekan "Saya dah bayar" (tanpa resit). Staff semak duit masuk dalam app bank.
import { notify, escHtml, json } from "../../lib/telegram.mjs";
import { readOrder } from "../../lib/order.mjs";

const seen = new Map();
export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host, origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);
  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  const o = readOrder(b?.token);
  if (!o) return json({ error: "Pesanan tak dikenali. Sila WhatsApp kami." }, 400);
  const n = (seen.get(o.id) || 0) + 1;
  seen.set(o.id, n);
  if (n > 1) return json({ ok: true, ulang: true }); // dah dimaklumkan, jangan spam group
  const pembayar = String(b?.pembayar ?? "").trim().slice(0, 80);
  const masa = new Date(Date.now() + 8 * 3600e3).toISOString().slice(11, 16);
  const text = [
    `💸 <b>Pelanggan kata DAH BAYAR RM${escHtml(o.jumlah)}</b> (DuitNow)`,
    `ID Order: <code>${escHtml(o.id)}</code>`,
    `Nama: ${escHtml(o.nama)} · ${escHtml(o.tel)}`,
    pembayar ? `Nama pembayar di bank: ${escHtml(pembayar)}` : "",
    `Ditekan pada: ${masa}`,
    "",
    `✅ <i>Buka app Maybank FIREA LABS, cari duit masuk RM${escHtml(o.jumlah)} sekitar ${masa}, baru pos. Resit mungkin tak dihantar.</i>`,
  ].filter((l, i, a) => l !== "" || a[i - 1] !== "").join("\n");
  try { const r = await notify(text); if (!r.ok && !r.skipped) console.error("Telegram gagal", "\n" + text); } catch (e) { console.error("Telegram ralat", e.message, "\n" + text); }
  return json({ ok: true });
};

export const config = { path: "/api/order-paid" };
