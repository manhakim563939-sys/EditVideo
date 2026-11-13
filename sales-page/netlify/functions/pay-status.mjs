// GET /api/pay-status  -> { online: true } bila kunci Billplz dah dimasukkan dalam Netlify.
import { settings, json } from "../../lib/billplz.mjs";

export default async () => {
  const c = settings();
  return json({ online: Boolean(c.apiKey && c.collectionId && c.xKey) });
};

export const config = { path: "/api/pay-status" };
