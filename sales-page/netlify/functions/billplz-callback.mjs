// POST /api/billplz-callback  (dipanggil oleh server Billplz selepas bayaran)
// Sahkan X Signature dan rekod dalam log fungsi Netlify. Rekod rasmi bayaran kekal di dashboard Billplz.
import { settings, verify } from "../../lib/billplz.mjs";

export default async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });
  const params = [...new URLSearchParams(await req.text()).entries()];
  const p = Object.fromEntries(params);
  if (!verify(params, settings().xKey)) {
    console.warn("Billplz callback: X Signature tak sah", p.id);
    return new Response("invalid signature", { status: 400 });
  }
  console.log(`Billplz callback: bil ${p.id} paid=${p.paid} state=${p.state} amount=${p.paid_amount} nama=${p.name}`);
  return new Response("OK", { status: 200 });
};

export const config = { path: "/api/billplz-callback" };
