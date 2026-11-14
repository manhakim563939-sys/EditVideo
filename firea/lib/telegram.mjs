// Hantar notifikasi ke Telegram (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID dalam Netlify > Environment variables).
// TELEGRAM_CHAT_ID boleh lebih dari satu, dipisahkan koma (cth. group staff + chat peribadi).
export const tgToken = () => process.env.TELEGRAM_BOT_TOKEN || "";
export const tgChat = () => process.env.TELEGRAM_CHAT_ID || "";
export const tgBotId = () => tgToken().split(":")[0] || "";

export const escHtml = s => String(s ?? "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

export const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

export async function tg(method, payload) {
  const res = await fetch(`https://api.telegram.org/bot${tgToken()}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json().catch(() => ({ ok: false }));
}

export async function notify(html) {
  if (!tgToken() || !tgChat()) return { ok: false, skipped: true };
  const chats = tgChat().split(",").map(s => s.trim()).filter(Boolean);
  const out = [];
  for (const chat_id of chats) out.push(await tg("sendMessage", { chat_id, text: html, parse_mode: "HTML", disable_web_page_preview: true }));
  return { ok: out.every(r => r.ok), results: out };
}
