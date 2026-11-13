// POST /api/order-notify  { pkg, negeri, nama, tel, alamat, poskod, sumber }
// Dipanggil bila pelanggan hantar order COD (sebelum WhatsApp dibuka) supaya order masuk group Telegram.
// Harga dikira semula di server. Order COD belum disahkan sehingga pelanggan hantar mesej WhatsApp.
import { quote, normMobile, json, STATES } from "../../lib/billplz.mjs";
import { notify, escHtml } from "../../lib/telegram.mjs";

const recent = new Map(); // had ringan setiap IP (hanya dalam instance yang sama)

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host;
  const origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);

  const ip = req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for") || "";
  const now = Date.now(), last = recent.get(ip) || [];
  const win = last.filter(t => now - t < 10 * 60 * 1000);
  if (win.length >= 5) return json({ error: "Terlalu banyak cubaan." }, 429);
  recent.set(ip, [...win, now]);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  if (b?.website) return json({ ok: true }); // perangkap bot
  const s = k => String(b?.[k] ?? "").trim().slice(0, 300);
  const nama = s("nama").slice(0, 120), tel = s("tel"), alamat = s("alamat"), poskod = s("poskod"), negeri = s("negeri");
  const q = quote(Number(b?.pkg), negeri);
  if (!q || !nama || !/^60\d{8,11}$/.test(normMobile(tel)) || !alamat || !/^\d{5}$/.test(poskod) || !STATES.includes(negeri))
    return json({ error: "Data order tak lengkap." }, 400);

  const repeat = s("sumber") === "repeat";
  const text = [
    `🛒 <b>Order COD baru RM${q.jumlah}</b>${repeat ? " · REPEAT" : ""}`,
    escHtml(q.nama) + (q.posRM ? ` (pos RM${q.posRM})` : " (pos percuma)"),
    "",
    `👤 ${escHtml(nama)}`,
    `📞 ${escHtml(tel)}`,
    `🏠 ${escHtml(`${alamat}, ${poskod} ${negeri}`)}`,
    "",
    "⚠️ <i>COD: tunggu pelanggan hantar WhatsApp / sahkan dulu sebelum pos.</i>",
  ].join("\n");
  try { await notify(text); } catch (e) { console.error("Telegram ralat", e.message); }
  return json({ ok: true });
};

export const config = { path: "/api/order-notify" };
