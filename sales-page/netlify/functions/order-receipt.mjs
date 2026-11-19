// POST /api/order-receipt  (multipart: token, resit=<gambar>)
// Pelanggan DuitNow muat naik resit; gambar dihantar ke group Telegram bersama ID Order yang disahkan.
import { json } from "../../lib/billplz.mjs";
import { notifyPhoto, escHtml } from "../../lib/telegram.mjs";
import { readOrder } from "../../lib/order.mjs";

const done = new Map();
export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const host = new URL(req.url).host, origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);
  let fd;
  try { fd = await req.formData(); } catch (_) { return json({ error: "Muat naik tak sah." }, 400); }
  const o = readOrder(fd.get("token"));
  if (!o) return json({ error: "Order tak dikenali. Sila WhatsApp resit kepada kami." }, 400);
  const file = fd.get("resit");
  if (!file || typeof file === "string" || !/^image\//.test(file.type || "")) return json({ error: "Sila pilih gambar resit (JPG/PNG)." }, 400);
  if (file.size > 5 * 1024 * 1024) return json({ error: "Gambar terlalu besar (maks 5MB)." }, 400);
  const n = (done.get(o.id) || 0) + 1;
  if (n > 3) return json({ error: "Resit untuk order ini dah diterima." }, 429);
  done.set(o.id, n);
  const caption = [
    `🧾 <b>Resit DuitNow</b>${n > 1 ? ` (muat naik ke-${n})` : ""}`,
    `ID Order: <code>${escHtml(o.id)}</code>`,
    `Jumlah perlu dibayar: <b>RM${escHtml(o.jumlah)}</b>`,
    `Nama: ${escHtml(o.nama)} · ${escHtml(o.tel)}`,
    "",
    "✅ <i>Semak duit RM" + escHtml(o.jumlah) + " dah masuk akaun LUNAS RESOURCES sebelum pos.</i>",
  ].join("\n");
  try {
    const r = await notifyPhoto(file, `resit-${o.id}.jpg`, caption);
    if (!r.ok && !r.skipped) { console.error("Telegram resit gagal", JSON.stringify(r).slice(0, 300)); return json({ error: "Tak dapat hantar resit sekarang. Sila WhatsApp resit kepada kami." }, 502); }
  } catch (e) { return json({ error: "Tak dapat hantar resit sekarang. Sila WhatsApp resit kepada kami." }, 502); }
  return json({ ok: true, orderId: o.id });
};

export const config = { path: "/api/order-receipt" };
