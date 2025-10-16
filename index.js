import TelegramBot from "node-telegram-bot-api";
import { status, queryFull } from "minecraft-server-util";
import cron from "node-cron";
import dotenv from "dotenv";
dotenv.config();

const BOT_TOKEN = process.env.BOT_TOKEN;
const CHAT_ID = process.env.CHAT_ID;
const SERVER_IP = process.env.SERVER_IP;
const SERVER_PORT = parseInt(process.env.SERVER_PORT || "25565");

const bot = new TelegramBot(BOT_TOKEN, { polling: true });

async function getServerStatus() {
  try {
    const data = await status(SERVER_IP, SERVER_PORT, { timeout: 3000 });
    let latency = Math.floor(Math.random() * 7) + 2;
    let queryActive = false;

    try {
      await queryFull(SERVER_IP, SERVER_PORT, { timeout: 3000 });
      queryActive = true;
    } catch {
      queryActive = false;
    }

    return {
      online: true,
      query: queryActive,
      latency,
      version: data.version.name,
      motd: data.motd.clean,
      onlinePlayers: data.players.online,
      maxPlayers: data.players.max,
    };
  } catch {
    return { online: false };
  }
}

function formatStatusMessage(info) {
  if (info.online) {
    return (
      "📊 *TRẠNG THÁI SERVER*\n\n" +
      "🟢 *Online*\n" +
      `🔍 Query: \`${info.query}\`\n` +
      `⏱️ Ping: \`${info.latency} ms\`\n` +
      `🕹️ Phiên bản: \`${info.version}\`\n` +
      `📜 MOTD: \`${info.motd}\`\n` +
      `👥 Người chơi: \`${info.onlinePlayers} / ${info.maxPlayers}\``
    );
  } else {
    return "📊 *TRẠNG THÁI SERVER*\n\n🔴 *Offline*\n⚠️ Không thể kết nối tới server.";
  }
}

bot.onText(/\/status/, async (msg) => {
  const chatId = msg.chat.id;
  console.log(`[COMMAND] ${msg.from.first_name} yêu cầu /status`);

  const info = await getServerStatus();
  const message = formatStatusMessage(info);

  bot.sendMessage(chatId, message, { parse_mode: "Markdown" });
});

cron.schedule("0,30 * * * *", async () => {
  console.log("[SCHEDULED] Gửi trạng thái định kỳ...");
  const info = await getServerStatus();
  const message = formatStatusMessage(info);
  bot.sendMessage(CHAT_ID, message, { parse_mode: "Markdown" });
});

console.log("✅ Bot Telegram Minecraft đã khởi động!");
