// GET /api/billplz-verify?billplz[id]=..&billplz[paid]=..&billplz[paid_at]=..&billplz[x_signature]=..
// Halaman /pesanan/ hantar semula query dari Billplz ke sini untuk disahkan.
import { json } from "../../lib/telegram.mjs";
import { settings, verify, billplz, parseDesc } from "../../lib/billplz.mjs";

export default async (req) => {
  const params = [...new URL(req.url).searchParams.entries()].filter(([k]) => k.startsWith("billplz["));
  const id = (params.find(([k]) => k === "billplz[id]") || [])[1] || "";
  if (!id || !verify(params, settings().xKey)) return json({ valid: false });
  const r = await billplz("/bills/" + encodeURIComponent(id));
  const d = r.ok ? r.data : {};
  return json({
    valid: true, billId: id, orderId: parseDesc(d.description).id,
    paid: r.ok ? d.paid === true : (params.find(([k]) => k === "billplz[paid]") || [])[1] === "true",
    amount: typeof d.amount === "number" ? d.amount / 100 : null,
    url: d.url || "",
  });
};

export const config = { path: "/api/billplz-verify" };
