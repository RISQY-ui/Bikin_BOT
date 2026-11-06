import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get("TOKEN")

# Simpan mode user: video / audio
user_mode = {}
# Simpan kualitas: sd / hd / fhd
user_quality = {}

def quality_label(user_id):
    q = user_quality.get(user_id, "hd")
    return {"sd": "📺 SD (480p - Hemat)", "hd": "📺 HD (720p)", "fhd": "📺 Full HD (1080p - Paling Jernih)"}[q]

def main_menu(user_id=None):
    keyboard = [
        [InlineKeyboardButton("🎬 Download Video", callback_data="mode_video"),
         InlineKeyboardButton("🎵 Download MP3 / Lagu", callback_data="mode_audio")],
        [InlineKeyboardButton("ℹ️ Info Video", callback_data="mode_info"),
         InlineKeyboardButton("❓ Bantuan", callback_data="help")],
        [InlineKeyboardButton("📺 Pilih Kualitas", callback_data="quality_menu")],
        [InlineKeyboardButton("📊 Cek Bot", callback_data="ping")],
    ]
    return InlineKeyboardMarkup(keyboard)

def quality_menu():
    keyboard = [
        [InlineKeyboardButton("📺 SD 480p - Hemat Kuota", callback_data="quality_sd")],
        [InlineKeyboardButton("📺 HD 720p - Standar Jernih ✅", callback_data="quality_hd")],
        [InlineKeyboardButton("📺 Full HD 1080p - Paling Jernih", callback_data="quality_fhd")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_mode[user_id] = "video"
    if user_id not in user_quality:
        user_quality[user_id] = "hd"
    name = update.effective_user.first_name or "Faris"
    text = (
        f"Halo {name}! 👋\n\n"
        f"Aku Bot Download PRO MAX-nya Faris 🔥\n\n"
        f"Mode sekarang: 🎬 VIDEO\n"
        f"Kualitas: {quality_label(user_id)}\n\n"
        f"Fiturku:\n"
        f"✅ Download TikTok tanpa watermark\n"
        f"✅ Download IG Reels / Post\n"
        f"✅ Download YouTube Shorts / Video\n"
        f"✅ Download Facebook Video\n"
        f"✅ Download MP3 / Lagu dari video\n"
        f"✅ Cek Info video tanpa download\n"
        f"✅ Pilih Kualitas SD / HD / Full HD\n\n"
        f"Cara pakai: tinggal kirim LINK-nya aja!\n"
        f"Atau pilih tombol di bawah:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 CARA PAKAI BOT\n\n"
        "1️⃣ Kirim link aja -> langsung download VIDEO\n"
        "2️⃣ Klik tombol 🎵 MP3 dulu baru kirim link -> download LAGU\n"
        "3️⃣ Klik tombol ℹ️ Info dulu baru kirim link -> cuma liat judul, durasi, views\n"
        "4️⃣ Klik tombol 📺 Pilih Kualitas dulu -> pilih SD / HD / Full HD\n\n"
        "Perintah cepat:\n"
        "/start - Buka menu\n"
        "/video - Mode Video\n"
        "/mp3 - Mode MP3 / Lagu\n"
        "/info - Mode Info\n"
        "/ping - Cek bot hidup atau nggak\n"
        "/about - Tentang bot\n\n"
        "Link yang didukung:\n"
        "TikTok, Instagram, YouTube, Facebook, Twitter/X, dll."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    else:
        await update.callback_query.edit_message_text(text, reply_markup=main_menu())

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    user_id = update.effective_user.id
    user_mode[user_id] = mode
    label = {"video": "🎬 VIDEO", "audio": "🎵 MP3 / LAGU", "info": "ℹ️ INFO VIDEO"}[mode]
    q = update.callback_query
    await q.answer(f"Mode diubah ke {label}")
    await q.edit_message_text(
        f"Mode sekarang: {label}\n\nSekarang kirim LINK-nya, Faris! 👇\n\nKirim link TikTok / IG / YouTube / FB.",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    if data == "mode_video":
        await set_mode(update, context, "video")
    elif data == "mode_audio":
        await set_mode(update, context, "audio")
    elif data == "mode_info":
        await set_mode(update, context, "info")
    elif data == "help":
        await help_cmd(update, context)
    elif data == "quality_menu":
        await update.callback_query.answer("Pilih kualitas video")
        await update.callback_query.edit_message_text(
            "📺 PILIH KUALITAS VIDEO\n\n"
            "SD 480p = Kecil, hemat kuota, cepet download\n"
            "HD 720p = Pas, jernih, ukuran sedang (Recommended)\n"
            "Full HD 1080p = Paling jernih, tapi file gede, kadang >50MB jadi gagal\n\n"
            "Kualitas kamu sekarang: " + quality_label(update.effective_user.id),
            reply_markup=quality_menu()
        )
    elif data in ("quality_sd", "quality_hd", "quality_fhd"):
        q = data.replace("quality_", "")
        user_quality[update.effective_user.id] = q
        label = quality_label(update.effective_user.id)
        await update.callback_query.answer(f"Kualitas jadi {label}")
        await update.callback_query.edit_message_text(
            f"Kualitas diubah ke: {label} ✅\n\nSekarang kirim LINK-nya, Faris! 👇",
            reply_markup=main_menu()
        )
    elif data == "back_menu":
        await update.callback_query.edit_message_text(
            "Balik ke menu utama ya! Kirim LINK-nya aja.",
            reply_markup=main_menu()
        )
    elif data == "ping":
        await update.callback_query.answer("Bot hidup! ✅")
        await update.callback_query.edit_message_text("✅ Bot HIDUP dan siap download!\n\nMode kamu masih sama, tinggal kirim link aja.", reply_markup=main_menu())

async def cmd_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode[update.effective_user.id] = "video"
    await update.message.reply_text("Mode diubah ke 🎬 VIDEO. Kirim linknya!", reply_markup=main_menu())

async def cmd_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = context.args[0]
        await handle_download(update, context, url, "audio")
        return
    user_mode[update.effective_user.id] = "audio"
    await update.message.reply_text("Mode diubah ke 🎵 MP3 / LAGU. Kirim linknya!", reply_markup=main_menu())

async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        url = context.args[0]
        await handle_download(update, context, url, "info")
        return
    user_mode[update.effective_user.id] = "info"
    await update.message.reply_text("Mode diubah ke ℹ️ INFO. Kirim linknya!", reply_markup=main_menu())

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 PONG! Bot hidup dan siap download! ✅")

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Download PRO MAX\n"
        "Dibuat oleh Faris + Tiara ❤️\n"
        "Versi: 3.0 - HD Update\n"
        "Powered by yt-dlp + python-telegram-bot\n\n"
        "Fitur: Video, MP3, Info, Pilih Kualitas HD, Auto Download"
    )

async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, mode: str):
    if "http" not in url:
        await update.message.reply_text("Kirim linknya ya, Faris. Contoh: https://www.tiktok.com/...")
        return
    status = await update.message.reply_text("⏳ Lagi aku proses... sabar ya")
    if mode == "info":
        ydl_opts = {'quiet': True, 'noplaylist': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            text = (
                f"ℹ️ INFO VIDEO\n\n"
                f"📌 Judul: {info.get('title','-')}\n"
                f"👤 Channel: {info.get('uploader','-')}\n"
                f"⏱️ Durasi: {info.get('duration',0)} detik\n"
                f"👀 Views: {info.get('view_count','-')}\n"
                f"❤️ Likes: {info.get('like_count','-')}\n"
                f"📅 Upload: {info.get('upload_date','-')}\n\n"
                f"Mau download? Klik tombol di bawah terus kirim link lagi."
            )
            await status.edit_text(text, reply_markup=main_menu())
        except Exception as e:
            await status.edit_text(f"Gagal ambil info 😢\nLinknya mungkin private.\nError: {e}")
        return
    if mode == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': 'audio_%(id)s.%(ext)s',
            'quiet': True, 'noplaylist': True,
            'max_filesize': 45 * 1024 * 1024,
        }
    else:
        q = user_quality.get(update.effective_user.id, "hd")
        fmt_map = {
            "sd": "best[height<=480][ext=mp4]/best[height<=480]/best",
            "hd": "best[height<=720][ext=mp4]/best[height<=720]/best",
            "fhd": "best[height<=1080][ext=mp4]/best[height<=1080]/best",
        }
        ydl_opts = {
            'format': fmt_map.get(q, fmt_map["hd"]),
            'outtmpl': 'download_%(id)s.%(ext)s',
            'quiet': True, 'noplaylist': True,
            'max_filesize': 45 * 1024 * 1024,
        }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mode == "audio":
                base = os.path.splitext(filename)[0]
                filename = base + ".mp3"
                if not os.path.exists(filename):
                    for f in os.listdir("."):
                        if f.startswith("audio_"):
                            filename = f
                            break
            title = info.get('title','Video')[:100]
        if mode == "audio":
            await update.message.reply_audio(audio=open(filename,'rb'), title=title, caption=f"🎵 {title}\nBerhasil download MP3!")
        else:
            qlabel = quality_label(update.effective_user.id)
            await update.message.reply_video(video=open(filename,'rb'), caption=f"Berhasil! 🎉\n{title}\nKualitas: {qlabel}")
        os.remove(filename)
        await status.delete()
        user_mode[update.effective_user.id] = "video"
    except Exception as e:
        await status.edit_text(
            "Gagal download 😢\n\nBiasanya karena:\n- Akunnya private\n- Videonya > 50MB / kepanjangan\n- Linknya salah / udah dihapus\n\nCoba link lain ya.",
            reply_markup=main_menu()
        )
        print(f"Error: {e}")

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    mode = user_mode.get(update.effective_user.id, "video")
    await handle_download(update, context, url, mode)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("video", cmd_video))
app.add_handler(CommandHandler("mp3", cmd_mp3))
app.add_handler(CommandHandler("info", cmd_info))
app.add_handler(CommandHandler("ping", cmd_ping))
app.add_handler(CommandHandler("about", cmd_about))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
print("Bot PRO MAX jalan...")
app.run_polling()
