import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo Faris! 👋\n\n"
        "Kirim aja linknya ke sini, aku download-in:\n"
        "✅ TikTok (tanpa watermark)\n"
        "✅ Instagram Reels / Post\n"
        "✅ YouTube Shorts / Video\n"
        "✅ Facebook Video\n\n"
        "Tinggal paste linknya aja!"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "http" not in url:
        await update.message.reply_text("Kirim linknya ya, Faris. Bukan teks biasa.")
        return
    status_msg = await update.message.reply_text("Lagi aku proses... ⏳ sabar ya")
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'download_%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'max_filesize': 45 * 1024 * 1024,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Video')[:100]
        await update.message.reply_video(video=open(filename, 'rb'), caption=f"Berhasil didownload! 🎉\n{title}")
        os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"Gagal download, Faris 😢\n\nBiasanya karena:\n- Akunnya private\n- Videonya > 50MB / kepanjangan\n- Linknya salah\n\nCoba link lain ya.")
        print(f"Error: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
print("Bot PRO jalan...")
app.run_polling()
