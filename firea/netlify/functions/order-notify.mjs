// POST /api/order-notify  { qty, negeri, nama, tel, alamat, poskod, bandar, bayaran, sumber }
// Dipanggil bila pelanggan tekan "Hantar Order" di website, supaya order masuk group Telegram.
// Harga dikira semula di server. Order belum sah sehingga pelanggan hantar mesej WhatsApp.
import { notify, escHtml, json } from "../../lib/telegram.mjs";
import { quote, normMobile } from "../../lib/order.mjs";

const recent = new Map(); // had ringan setiap IP (dalam instance yang sama)

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host;
  const origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);

  const ip = req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for") || "";
  const now = Date.now(), win = (recent.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
  if (win.length >= 5) return json({ error: "Terlalu banyak cubaan." }, 429);
  recent.set(ip, [...win, now]);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  if (b?.website) return json({ ok: true }); // perangkap bot
  const s = (k, n = 300) => String(b?.[k] ?? "").trim().slice(0, n);
  const nama = s("nama", 120), tel = s("tel", 30), alamat = s("alamat"), poskod = s("poskod", 5), bandar = s("bandar", 80), negeri = s("negeri", 40);
  const bayaran = /transfer/i.test(s("bayaran")) ? "Online Transfer" : "COD";
  const q = quote(Number(b?.qty), negeri);
  if (!q || !nama || !/^60\d{8,11}$/.test(normMobile(tel)) || !alamat || !/^\d{5}$/.test(poskod))
    return json({ error: "Data order tak lengkap." }, 400);

  const sumber = s("sumber", 20) === "shop" ? "fireadeodorant.com/shop" : "fireadeodorant.com";
  const waLink = `https://wa.me/${normMobile(tel)}`;
  const text = [
    `🛒 <b>Order Firea baru · RM${q.jumlah}</b>`,
    `${q.qty} botol RM${q.price} · ${q.pos ? `pos RM${q.pos}` : "pos PERCUMA"} · ${bayaran}`,
    "",
    `Pakej: Firea (${q.qty} botol) RM${q.price}`,
    `Jumlah: *RM${q.jumlah}*`,
    `Bayaran: ${bayaran}`,
    `Nama: ${escHtml(nama)}`,
    `Tel: ${escHtml(tel)}`,
    `Alamat: ${escHtml(`${alamat}, ${poskod} ${bandar}, ${negeri}`)}`,
    "",
    `💬 <a href="${waLink}">WhatsApp pelanggan</a> · dari ${sumber}`,
    "⚠️ <i>Belum sah: tunggu pelanggan hantar mesej WhatsApp / sahkan dulu sebelum pos.</i>",
  ].join("\n");
  try { await notify(text); } catch (e) { console.error("Telegram ralat", e.message); }
  return json({ ok: true });
};

export const config = { path: "/api/order-notify" };
