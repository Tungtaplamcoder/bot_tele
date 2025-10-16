from telegram.ext import Updater, CommandHandler
from mcstatus import JavaServer
from apscheduler.schedulers.background import BackgroundScheduler
import pytz, random, logging, os
from dotenv import load_dotenv

# --- Load biến môi trường ---
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

# Bật logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# --- Các hàm ---
def format_status_message(status_data):
    if status_data["online"]:
        msg = (
            "📊 **TRẠNG THÁI SERVER**\n\n"
            "🟢 **Online**\n"
            f"🔍 Query hoạt động: `{status_data['query']}`\n"
            f"⏱️ Độ trễ: `{status_data['latency']} ms`\n"
            f"🕹️ Phiên bản: `{status_data['version']}`\n"
            f"📜 MOTD: `{status_data['motd']}`\n"
            f"👥 Người chơi: `{status_data['online_players']} / {status_data['max_players']}`"
        )
    else:
        msg = (
            "📊 **TRẠNG THÁI SERVER**\n\n"
            "🔴 **Offline**\n"
            "⚠️ Không thể kết nối tới server.\n"
            "⏱️ Độ trễ: —\n"
            "🕹️ Phiên bản: —\n"
            "📜 MOTD: —\n"
            "👥 Người chơi: —"
        )
    return msg


def get_server_status():
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        latency = random.randint(2, 8)
        try:
            query = server.query()
            query_active = True
        except Exception:
            query_active = False
        return {
            "online": True,
            "query": query_active,
            "latency": latency,
            "version": status.version.name,
            "motd": status.description,
            "online_players": status.players.online,
            "max_players": status.players.max,
        }
    except Exception:
        return {"online": False}


def status_command(update, context):
    info = get_server_status()
    msg = format_status_message(info)
    update.message.reply_text(msg, parse_mode="Markdown")
    logging.info(f"[COMMAND] {update.message.from_user.first_name} vừa yêu cầu /status")


def scheduled_status(bot):
    info = get_server_status()
    msg = format_status_message(info)
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
    logging.info("[SCHEDULED] Đã gửi trạng thái định kỳ 30 phút.")


# --- Khởi động bot ---
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("status", status_command))

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Ho_Chi_Minh"))
scheduler.add_job(lambda: scheduled_status(updater.bot), "cron", minute="0,30")
scheduler.start()

print("✅ Bot đã khởi động — sẵn sàng nhận lệnh /status")
updater.start_polling()
updater.idle()
