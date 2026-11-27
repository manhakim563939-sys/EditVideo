// POST /api/billplz-callback  (dipanggil oleh server Billplz selepas bayaran)
// Sahkan X Signature, kemudian hantar order yang DIBAYAR ke group Telegram.
import { notify, escHtml } from "../../lib/telegram.mjs";
import { settings, verify, billplz, parseDesc } from "../../lib/billplz.mjs";
import { sumberLabel } from "../../lib/order.mjs";

const sent = new Set(); // Billplz boleh panggil lebih sekali untuk bil yang sama
export default async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  const params = [...new URLSearchParams(await req.text()).entries()];
  const p = Object.fromEntries(params);
  if (!verify(params, settings().xKey)) {
    console.warn("Billplz callback: X Signature tak sah", p.id);
    return new Response("invalid signature", { status: 400 });
  }
  console.log(`Billplz callback: bil ${p.id} paid=${p.paid} state=${p.state} amount=${p.paid_amount}`);
  if (p.paid !== "true" || sent.has(p.id)) return new Response("OK");
  sent.add(p.id);

  let bill = {};
  try { const r = await billplz("/bills/" + encodeURIComponent(p.id)); if (r.ok) bill = r.data || {}; } catch (_) {}
  const d = parseDesc(bill.description);
  const rm = (Number(p.paid_amount || bill.paid_amount || 0) / 100).toFixed(2).replace(/\.00$/, "");
  const tel = bill.reference_1 || p.mobile || "";
  const wa = String(tel).replace(/\D/g, "").replace(/^0/, "60");
  const text = [
    `💰 <b>Order ONLINE · DIBAYAR RM${escHtml(rm)}</b>${settings().sandbox ? " (UJIAN SANDBOX)" : ""}`,
    d.id ? `ID Order: <code>${escHtml(d.id)}</code>` : `ID Bil: <code>${escHtml(p.id)}</code>`,
    "",
    d.qty ? `Pakej: Firea (${d.qty} botol)` : `Pakej: ${escHtml(bill.description || "-")}`,
    ...(d.diskaun ? [`Voucher: ${escHtml(d.voucher)} (-RM${d.diskaun})`] : []),
    `Jumlah: *RM${escHtml(rm)}*`,
    `Bayaran: FPX / Kad (Billplz) - SUDAH DIBAYAR`,
    "",
    `Nama: ${escHtml(p.name || bill.name || "")}`,
    `Tel: ${escHtml(tel)}`,
    `Alamat: ${escHtml(bill.reference_2 || "-")}`,
    "",
    wa ? `💬 <a href="https://wa.me/${wa}">WhatsApp pelanggan</a> · dari ${sumberLabel(d.sumber)}` : "",
    `✅ <i>Duit dah disahkan oleh Billplz. Boleh terus pos.</i>`,
  ].filter((l, i, a) => l !== "" || a[i - 1] !== "").join("\n");
  try {
    const r = await notify(text);
    if (!r.ok && !r.skipped) console.error("Telegram gagal", JSON.stringify(r).slice(0, 300), "\nORDER TAK SAMPAI TELEGRAM:\n" + text);
  } catch (e) { console.error("Telegram ralat", e.message, "\nORDER TAK SAMPAI TELEGRAM:\n" + text); }
  return new Response("OK");
};

export const config = { path: "/api/billplz-callback" };
