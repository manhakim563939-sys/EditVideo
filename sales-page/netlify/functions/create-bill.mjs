// POST /api/create-bill  { pkg, negeri, nama, tel, email?, alamat, poskod, sumber? }
// Cipta bil Billplz dengan harga dikira di server, kemudian pulangkan URL bayaran.
import { quote, settings, normMobile, billplz, json, STATES } from "../../lib/billplz.mjs";

export default async (req) => {
  if (req.method !== "POST") return json({ error: "Kaedah tak dibenarkan." }, 405);
  const c = settings();
  if (!c.apiKey || !c.collectionId) return json({ error: "Bayaran online belum disediakan. Sila pilih COD." }, 503);

  let b;
  try { b = await req.json(); } catch (_) { return json({ error: "Data tak sah." }, 400); }
  const s = k => String(b?.[k] ?? "").trim();
  const nama = s("nama").slice(0, 120), tel = s("tel"), alamat = s("alamat"), poskod = s("poskod"), negeri = s("negeri"), email = s("email");
  const q = quote(Number(b?.pkg), negeri);
  const mobile = normMobile(tel);
  const bad = [];
  if (!q) bad.push("pakej");
  if (!nama) bad.push("nama");
  if (!/^60\d{8,11}$/.test(mobile)) bad.push("no. telefon");
  if (!alamat) bad.push("alamat");
  if (!/^\d{5}$/.test(poskod)) bad.push("poskod");
  if (!STATES.includes(negeri)) bad.push("negeri");
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) bad.push("email");
  if (bad.length) return json({ error: "Sila semak: " + bad.join(", ") + "." }, 400);

  const origin = new URL(req.url).origin;
  const sumber = s("sumber") === "repeat" ? "Repeat" : "Website";
  const body = {
    collection_id: c.collectionId,
    mobile,
    ...(email ? { email } : {}),
    name: nama,
    amount: q.jumlah * 100,
    description: `Jus Bidara Hitam: ${q.nama} (${sumber})`.slice(0, 200),
    callback_url: origin + "/api/billplz-callback",
    redirect_url: origin + "/terima-kasih/",
    reference_1_label: "Telefon",
    reference_1: tel.slice(0, 120),
    reference_2_label: "Alamat",
    reference_2: `${alamat}, ${poskod} ${negeri}`.replace(/\s+/g, " ").slice(0, 120),
  };
  const r = await billplz("/bills", { method: "POST", body });
  if (!r.ok || !r.data?.url) {
    console.error("Billplz create bill gagal", r.status, JSON.stringify(r.data).slice(0, 500));
    return json({ error: "Tak dapat sediakan bayaran sekarang. Cuba lagi atau pilih COD." }, 502);
  }
  return json({ url: r.data.url, id: r.data.id, jumlah: q.jumlah });
};

export const config = { path: "/api/create-bill" };
