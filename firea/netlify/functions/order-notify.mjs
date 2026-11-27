// POST /api/order-notify  { qty, negeri, nama, tel, alamat, poskod, bandar, bayar: "COD" | "DUITNOW", sumber }
// Order COD / DuitNow QR dari website. Harga dikira semula di server, order diberi nombor rasmi,
// dihantar ke group Telegram, dan token dipulangkan untuk muat naik resit DuitNow.
import { notify, escHtml, json } from "../../lib/telegram.mjs";
import { quote, normMobile, newOrderId, signOrder, sumberLabel } from "../../lib/order.mjs";

const recent = new Map();   // had cubaan setiap IP (dalam instance yang sama)
const lastByTel = new Map(); // elak order pendua (nombor + pakej + cara bayar) dalam 10 minit

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host;
  const origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);

  const ip = req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for") || "";
  const now = Date.now(), win = (recent.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
  if (win.length >= 6) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar atau WhatsApp kami." }, 429);
  recent.set(ip, [...win, now]);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  if (b?.website) return json({ ok: true }); // perangkap bot
  const s = (k, n = 300) => String(b?.[k] ?? "").trim().slice(0, n);
  const nama = s("nama", 120), tel = s("tel", 30), alamat = s("alamat"), poskod = s("poskod", 5), bandar = s("bandar", 80), negeri = s("negeri", 40);
  const bayar = /duitnow|qr/i.test(s("bayar")) ? "DUITNOW" : "COD";
  const q = quote(Number(b?.qty), negeri, s("kod", 30));
  const mobile = normMobile(tel);
  if (!q || !nama || !/^60\d{8,11}$/.test(mobile) || !alamat || !/^\d{5}$/.test(poskod))
    return json({ error: "Maklumat order tak lengkap. Semak nama, telefon, alamat, poskod dan negeri." }, 400);

  const dupKey = `${mobile}|${q.qty}|${bayar}`;
  const prev = lastByTel.get(dupKey);
  if (prev && now - prev.at < 10 * 60 * 1000) return json({ ok: true, ...prev.res, pendua: true });

  const id = newOrderId();
  const sumber = sumberLabel(s("sumber", 20));
  const label = bayar === "DUITNOW" ? "DuitNow QR" : "COD";
  const text = [
    bayar === "DUITNOW" ? `🟣 <b>Order DuitNow QR · RM${q.jumlah}</b>` : `🛒 <b>Order COD · RM${q.jumlah}</b>`,
    `ID Order: <code>${id}</code>`,
    "",
    `Pakej: Firea (${q.qty} botol) RM${q.price}`,
    ...(q.diskaun ? [`Voucher: ${q.voucher} (-RM${q.diskaun})`] : []),
    `Postage: ${q.pos ? "RM" + q.pos : "PERCUMA"}`,
    `Jumlah: *RM${q.jumlah}*`,
    `Bayaran: ${label}`,
    "",
    `Nama: ${escHtml(nama)}`,
    `Tel: ${escHtml(tel)}`,
    `Alamat: ${escHtml(`${alamat}, ${poskod} ${bandar}, ${negeri}`)}`,
    "",
    `💬 <a href="https://wa.me/${mobile}">WhatsApp pelanggan</a> · dari ${sumber}`,
    bayar === "DUITNOW"
      ? "⏳ <i>Tunggu pelanggan tekan \"Saya dah bayar\" atau hantar resit (akan masuk di sini). Semak duit masuk akaun FIREA LABS sebelum pos.</i>"
      : "📞 <i>COD: telefon / WhatsApp pelanggan untuk sahkan sebelum pos.</i>",
  ].join("\n");
  try {
    const r = await notify(text);
    if (!r.ok && !r.skipped) console.error("Telegram gagal", JSON.stringify(r).slice(0, 300), "\nORDER TAK SAMPAI TELEGRAM:\n" + text);
  } catch (e) { console.error("Telegram ralat", e.message, "\nORDER TAK SAMPAI TELEGRAM:\n" + text); }

  const res = { orderId: id, jumlah: q.jumlah, diskaun: q.diskaun, voucher: q.voucher, qty: q.qty, harga: q.price, pos: q.pos, bayar,
    token: signOrder({ id, jumlah: q.jumlah, nama, tel, bayar }) };
  lastByTel.set(dupKey, { at: now, res });
  return json({ ok: true, ...res });
};

export const config = { path: "/api/order-notify" };
