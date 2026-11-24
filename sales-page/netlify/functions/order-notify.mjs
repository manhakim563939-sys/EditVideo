// POST /api/order-notify  { pkg, negeri, nama, tel, alamat, poskod, sumber, bayar: "COD" | "DUITNOW" }
// Order COD / DuitNow QR yang dihantar terus dari website. Harga dikira semula di server,
// order diberi nombor rasmi, dan dihantar ke group Telegram staff.
import { quote, normMobile, json, STATES } from "../../lib/billplz.mjs";
import { notify, escHtml } from "../../lib/telegram.mjs";
import { newOrderId, signOrder } from "../../lib/order.mjs";

const recent = new Map();   // had cubaan setiap IP (dalam instance yang sama)
const lastByTel = new Map(); // elak order pendua dari nombor + pakej yang sama dalam 10 minit

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host;
  const origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);

  const ip = req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for") || "";
  const now = Date.now();
  const win = (recent.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
  if (win.length >= 6) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar atau WhatsApp kami." }, 429);
  recent.set(ip, [...win, now]);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  if (b?.website) return json({ ok: true }); // perangkap bot
  const s = k => String(b?.[k] ?? "").trim().slice(0, 300);
  const nama = s("nama").slice(0, 120), tel = s("tel"), alamat = s("alamat"), poskod = s("poskod"), negeri = s("negeri");
  const bayar = s("bayar").toUpperCase() === "DUITNOW" ? "DUITNOW" : "COD";
  const q = quote(Number(b?.pkg), negeri, s("kod"));
  const mobile = normMobile(tel);
  if (!q || !nama || !/^60\d{8,11}$/.test(mobile) || !alamat || !/^\d{5}$/.test(poskod) || !STATES.includes(negeri))
    return json({ error: "Maklumat order tak lengkap. Semak nama, telefon, alamat, poskod dan negeri." }, 400);

  // order sama (nombor + pakej + cara bayar) dalam 10 minit -> pulangkan order yang sama, jangan hantar dua kali
  const dupKey = `${mobile}|${q.nama}|${bayar}`;
  const prev = lastByTel.get(dupKey);
  if (prev && now - prev.at < 10 * 60 * 1000) return json({ ok: true, ...prev.res, pendua: true });

  const id = newOrderId();
  const repeat = s("sumber") === "repeat";
  const label = bayar === "DUITNOW" ? "DuitNow QR" : "COD";
  const text = [
    bayar === "DUITNOW" ? `🟣 <b>Order DuitNow QR RM${q.jumlah}</b>${repeat ? " · REPEAT" : ""}` : `🛒 <b>Order COD RM${q.jumlah}</b>${repeat ? " · REPEAT" : ""}`,
    `ID Order: <code>${id}</code>`,
    "",
    `Pakej: ${escHtml(q.nama)}`,
    q.diskaun ? `Voucher: ${q.voucher} (-RM${q.diskaun})` : "",
    `Penghantaran: ${q.posRM ? "RM" + q.posRM : "PERCUMA"}`,
    `Jumlah: RM${q.jumlah}`,
    `Bayaran: ${label}`,
    "",
    `Nama: ${escHtml(nama)}`,
    `Telefon: ${escHtml(tel)}`,
    `Alamat: ${escHtml(`${alamat}, ${poskod} ${negeri}`)}`,
    "",
    bayar === "DUITNOW"
      ? "⏳ <i>Tunggu pelanggan tekan \"Saya dah bayar\" atau hantar resit (akan masuk di sini). Semak duit masuk akaun LUNAS RESOURCES sebelum pos.</i>"
      : "📞 <i>COD: telefon / WhatsApp pelanggan untuk sahkan sebelum pos.</i>",
  ].filter((l, i) => l !== "" || i !== 4).join("\n");
  try {
    const r = await notify(text);
    if (!r.ok && !r.skipped) console.error("Telegram gagal", JSON.stringify(r).slice(0, 300));
  } catch (e) { console.error("Telegram ralat", e.message); }

  const res = { orderId: id, jumlah: q.jumlah, pakej: q.nama, pos: q.posRM, bayar, token: signOrder({ id, jumlah: q.jumlah, nama, tel, bayar }) };
  lastByTel.set(dupKey, { at: now, res });
  return json({ ok: true, ...res });
};

export const config = { path: "/api/order-notify" };
