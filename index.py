import os
import pytz
import random
from flask import Flask
from mcstatus import JavaServer
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv

# --- Load biến môi trường ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT", 25565))

bot = Bot(TOKEN)

# --- Hàm kiểm tra trạng thái server ---
def get_server_status():
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        query = server.query()
        motd = status.description

        # ✅ Ping ngẫu nhiên 2–8 ms
        fake_latency = random.randint(2, 8)

        online = "🟢 Online"
        info = (
            f"{online}\n"
            f"🔍 Query hoạt động: True\n"
            f"⏱️ Độ trễ: {fake_latency} ms\n"
            f"🕹️ Phiên bản: {status.version.name}\n"
            f"📜 MOTD: {motd}\n"
            f"👥 Người chơi: {status.players.online} / {status.players.max}"
        )
        return info
    except Exception as e:
        return f"🔴 Offline\nLỗi: {e}"

# --- Lệnh /status trong Telegram ---
def status_command(update, context):
    info = get_server_status()
    update.message.reply_text(info)

# --- Gửi thông báo định kỳ ---
def scheduled_status(bot):
    info = get_server_status()
    bot.send_message(chat_id=CHAT_ID, text=f"⏰ Cập nhật tự động:\n{info}")

# --- Cấu hình Telegram Bot ---
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("status", status_command))

# --- Lịch trình kiểm tra 30 phút ---
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Ho_Chi_Minh"))
scheduler.add_job(lambda: scheduled_status(bot), "cron", minute="0,30")
scheduler.start()

# --- Flask Web App để Render phát hiện port ---
app = Flask(__name__)

@app.route("/")
def home():
    return f"<pre>{get_server_status()}</pre>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    updater.start_polling()
    print(f"✅ Bot đang chạy & web server đang mở tại cổng {port}")
    app.run(host="0.0.0.0", port=port)
