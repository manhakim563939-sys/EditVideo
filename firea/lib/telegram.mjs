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

// Bila group Telegram dinaik taraf jadi supergroup, ID group bertukar (-100...). Telegram beri ID baru dalam
// migrate_to_chat_id; kita cuba semula ke ID itu supaya order tak hilang (kemas kini TELEGRAM_CHAT_ID bila sempat).
const moved = r => r && !r.ok && r.parameters && r.parameters.migrate_to_chat_id;
const chatList = () => tgChat().split(",").map(s => s.trim()).filter(Boolean);

export async function notify(html) {
  if (!tgToken() || !tgChat()) return { ok: false, skipped: true };
  const out = [];
  for (const chat_id of chatList()) {
    const send = id => tg("sendMessage", { chat_id: id, text: html, parse_mode: "HTML", disable_web_page_preview: true });
    let r = await send(chat_id);
    if (moved(r)) { console.warn(`TELEGRAM_CHAT_ID ${chat_id} dah bertukar ke ${r.parameters.migrate_to_chat_id}. Kemas kini dalam Netlify.`); r = await send(r.parameters.migrate_to_chat_id); }
    out.push(r);
  }
  return { ok: out.every(r => r.ok), results: out };
}

export async function notifyPhoto(blob, filename, captionHtml) {
  if (!tgToken() || !tgChat()) return { ok: false, skipped: true };
  const out = [];
  for (const chat_id of chatList()) {
    const send = async id => {
      const fd = new FormData();
      fd.append("chat_id", id);
      fd.append("caption", captionHtml.slice(0, 1000));
      fd.append("parse_mode", "HTML");
      fd.append("photo", blob, filename);
      const res = await fetch(`https://api.telegram.org/bot${tgToken()}/sendPhoto`, { method: "POST", body: fd });
      return res.json().catch(() => ({ ok: false }));
    };
    let r = await send(chat_id);
    if (moved(r)) r = await send(r.parameters.migrate_to_chat_id);
    out.push(r);
  }
  return { ok: out.every(r => r.ok), results: out };
}
