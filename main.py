import os
import threading
import tempfile
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 🟢 متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")
PORT = int(os.environ.get("PORT", 10000))

# ✅ Dummy Web Server لحل مشكلة Render
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', PORT), DummyHandler)
    server.serve_forever()

# ✅ أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 أرسل اسم الأغنية التي تريد تحميلها MP3 من يوتيوب")

async def search_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text("🔍 جاري البحث عن الأغنية...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            title = info.get("title", "Unknown")

            await update.message.reply_audio(audio=open(file_path, 'rb'), title=title)
            os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء التحميل: {str(e)}")

# ✅ تشغيل التطبيق مع Webhook
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_and_send))

    # بدء بوابة وهمية في خلفية السيرفر
    threading.Thread(target=run_dummy_server).start()

    # تشغيل Webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{APP_URL}/{BOT_TOKEN}"
    )

if __name__ == '__main__':
    main()
