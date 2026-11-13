// GET /api/billplz-verify?billplz[id]=..&billplz[paid]=..&billplz[paid_at]=..&billplz[x_signature]=..
// Halaman terima kasih hantar semula query dari Billplz ke sini untuk disahkan.
import { settings, verify, billplz, json } from "../../lib/billplz.mjs";

export default async (req) => {
  const params = [...new URL(req.url).searchParams.entries()].filter(([k]) => k.startsWith("billplz["));
  const id = (params.find(([k]) => k === "billplz[id]") || [])[1] || "";
  if (!id || !verify(params, settings().xKey)) return json({ valid: false });
  const r = await billplz("/bills/" + encodeURIComponent(id));
  const d = r.ok ? r.data : {};
  return json({
    valid: true,
    id,
    paid: d.paid === true || (params.find(([k]) => k === "billplz[paid]") || [])[1] === "true",
    amount: typeof d.paid_amount === "number" ? d.paid_amount / 100 : typeof d.amount === "number" ? d.amount / 100 : null,
    description: d.description || "",
  });
};

export const config = { path: "/api/billplz-verify" };
