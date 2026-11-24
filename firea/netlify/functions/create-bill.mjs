// POST /api/create-bill  { qty, negeri, nama, tel, alamat, poskod, bandar, sumber }
// Bayaran online (FPX / kad) melalui Billplz. Harga dikira di server, order diberi nombor,
// pelanggan dihantar ke halaman bayaran Billplz dan kembali ke /pesanan/?id=...
import { json } from "../../lib/telegram.mjs";
import { quote, normMobile, newOrderId, signOrder, STATES } from "../../lib/order.mjs";
import { settings, ready, billplz, describe } from "../../lib/billplz.mjs";

const recent = new Map();
export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  if (!ready()) return json({ error: "Bayaran online belum dibuka. Sila pilih COD." }, 503);
  const host = new URL(req.url).host, origin = req.headers.get("origin") || "";
  if (origin && !origin.endsWith("//" + host)) return json({ error: "Tak dibenarkan." }, 403);

  const ip = req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for") || "";
  const now = Date.now(), win = (recent.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
  if (win.length >= 8) return json({ error: "Terlalu banyak cubaan. Cuba lagi sebentar atau WhatsApp kami." }, 429);
  recent.set(ip, [...win, now]);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  if (b?.website) return json({ error: "Tak dibenarkan." }, 400);
  const s = (k, n = 300) => String(b?.[k] ?? "").trim().slice(0, n);
  const nama = s("nama", 120), tel = s("tel", 30), alamat = s("alamat"), poskod = s("poskod", 5), bandar = s("bandar", 80), negeri = s("negeri", 40);
  const q = quote(Number(b?.qty), negeri);
  const mobile = normMobile(tel);
  if (!q || !STATES.includes(negeri) || !nama || !/^60\d{8,11}$/.test(mobile) || !alamat || !/^\d{5}$/.test(poskod))
    return json({ error: "Maklumat order tak lengkap. Semak nama, telefon, alamat, poskod dan negeri." }, 400);

  const id = newOrderId();
  const base = new URL(req.url).origin;
  const r = await billplz("/bills", { method: "POST", body: {
    collection_id: settings().collectionId,
    mobile,
    name: nama,
    amount: q.jumlah * 100,
    description: describe(q.qty, id, s("sumber", 20) === "shop" ? "shop" : "website"),
    callback_url: base + "/api/billplz-callback",
    redirect_url: base + "/pesanan/?id=" + encodeURIComponent(id),
    reference_1_label: "Telefon",
    reference_1: tel,
    reference_2_label: "Alamat",
    reference_2: `${alamat}, ${poskod} ${bandar}, ${negeri}`.replace(/\s+/g, " ").slice(0, 120),
  } });
  if (!r.ok || !r.data?.url) {
    console.error("Billplz create bill gagal", r.status, JSON.stringify(r.data).slice(0, 500));
    return json({ error: "Tak dapat buka bayaran online sekarang. Sila cuba lagi atau pilih COD." }, 502);
  }
  return json({ ok: true, orderId: id, url: r.data.url, billId: r.data.id, jumlah: q.jumlah, qty: q.qty, harga: q.price, pos: q.pos,
    bayar: "ONLINE", token: signOrder({ id, jumlah: q.jumlah, nama, tel, bayar: "ONLINE" }) });
};

export const config = { path: "/api/create-bill" };
