// GET /api/telegram-test?bot=<nombor ID bot>
// Bantu tetapan: tanpa TELEGRAM_CHAT_ID -> senaraikan chat ID yang dah mesej bot.
// Dengan TELEGRAM_CHAT_ID -> hantar mesej ujian. "bot" mesti sama dengan nombor di depan token bot (perlindungan ringan).
import { tg, tgToken, tgChat, tgBotId, notify } from "../../lib/telegram.mjs";
import { json } from "../../lib/billplz.mjs";

export default async (req) => {
  if (!tgToken()) return json({ error: "TELEGRAM_BOT_TOKEN belum dimasukkan dalam Netlify." }, 503);
  const bot = new URL(req.url).searchParams.get("bot") || "";
  if (bot !== tgBotId()) return json({ error: "Nombor bot tak sepadan. Guna nombor di depan tanda : dalam token bot." }, 403);

  if (!tgChat()) {
    const r = await tg("getUpdates", { limit: 50 });
    const chats = {};
    for (const u of r.result || []) {
      const c = (u.message || u.channel_post || u.my_chat_member || {}).chat;
      if (c) chats[c.id] = { chat_id: String(c.id), nama: c.title || [c.first_name, c.last_name].filter(Boolean).join(" ") || c.username || "", jenis: c.type };
    }
    const list = Object.values(chats);
    return json({
      langkah: list.length ? "Salin chat_id anda di bawah dan masukkan sebagai TELEGRAM_CHAT_ID dalam Netlify, kemudian Trigger deploy." : "Belum ada mesej. Buka bot anda di Telegram, tekan Start / hantar 'hai', kemudian muat semula halaman ini.",
      chats: list,
    });
  }
  const r = await notify("✅ <b>Ujian berjaya!</b>\nNotifikasi bayaran Jus Bidara Hitam akan masuk di sini.");
  return json({ hantar: r.ok ? "Mesej ujian dah dihantar ke Telegram." : "Gagal hantar. Semak TELEGRAM_CHAT_ID.", butiran: r.ok ? undefined : r.results });
};

export const config = { path: "/api/telegram-test" };
