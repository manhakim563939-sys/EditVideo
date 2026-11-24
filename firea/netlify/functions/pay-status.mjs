// GET /api/pay-status -> { online: true } bila kunci Billplz dah dimasukkan dalam Netlify.
import { json } from "../../lib/telegram.mjs";
import { ready } from "../../lib/billplz.mjs";
export default async () => json({ online: ready() });
export const config = { path: "/api/pay-status" };
