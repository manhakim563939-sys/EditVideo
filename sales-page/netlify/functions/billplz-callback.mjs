// POST /api/billplz-callback  (dipanggil oleh server Billplz selepas bayaran)
// Sahkan X Signature, kemudian hantar notifikasi Telegram bila bayaran berjaya.
import { settings, verify, billplz } from "../../lib/billplz.mjs";
import { notify, escHtml } from "../../lib/telegram.mjs";

export default async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  const params = [...new URLSearchParams(await req.text()).entries()];
  const p = Object.fromEntries(params);
  if (!verify(params, settings().xKey)) {
    console.warn("Billplz callback: X Signature tak sah", p.id);
    return new Response("invalid signature", { status: 400 });
  }
  console.log(`Billplz callback: bil ${p.id} paid=${p.paid} state=${p.state} amount=${p.paid_amount} nama=${p.name}`);

  if (p.paid === "true") {
    // Ambil butiran penuh bil (pakej, telefon, alamat) untuk notifikasi.
    let bill = {};
    try { const r = await billplz("/bills/" + encodeURIComponent(p.id)); if (r.ok) bill = r.data || {}; } catch (_) {}
    const rm = (Number(p.paid_amount || bill.paid_amount || 0) / 100).toFixed(2).replace(/\.00$/, "");
    const desc = bill.description || "";
    const vc = desc.match(/voucher (\S+) -RM(\d+)/);
    const text = [
      `💰 <b>Bayaran online DIBAYAR RM${escHtml(rm)}</b>${settings().sandbox ? " (UJIAN SANDBOX)" : ""}`,
      `ID Bil: <code>${escHtml(p.id)}</code>`,
      "",
      `Pakej: ${escHtml(desc.replace(/^Jus Bidara Hitam:\s*/, "").replace(/\s*\((Website|Repeat)[^)]*\)$/, ""))}`,
      vc ? `Voucher: ${escHtml(vc[1])} (-RM${vc[2]})` : null,
      `Jumlah: RM${escHtml(rm)}`,
      `Bayaran: Online (Billplz) - DIBAYAR`,
      "",
      `Nama: ${escHtml(p.name || bill.name)}`,
      `Telefon: ${escHtml(bill.reference_1 || p.mobile)}`,
      `Alamat: ${escHtml(bill.reference_2 || "-")}`,
      "",
      `🕒 ${escHtml(p.paid_at || "")}`,
      p.url ? `🔗 ${escHtml(p.url)}` : "",
    ].filter(l => l !== null).filter((l, i, a) => l !== "" || (a[i - 1] !== "" && i < a.length - 1)).join("\n");
    try {
      const r = await notify(text);
      if (!r.ok && !r.skipped) console.error("Telegram gagal", JSON.stringify(r).slice(0, 300));
    } catch (e) { console.error("Telegram ralat", e.message); }
  }
  return new Response("OK", { status: 200 });
};

export const config = { path: "/api/billplz-callback" };
