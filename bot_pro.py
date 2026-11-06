import os
import re
import json
import random
import asyncio
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder, CommandHandler, MessageHandler,
CallbackQueryHandler, ContextTypes, filters,
)

========================= CONFIG =========================

TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_DOWNLOAD_MB = 45
MAX_BATCH = 5
MAX_HISTORY = 10
MAX_MEMORY_MESSAGES = 10

user_mode = {}
user_quality = {}
user_history = {}
user_stats = {}
chat_memory = {}

MODES = {
"video": "🎬 VIDEO", "audio": "🎵 MP3", "info": "ℹ️ INFO",
"thumb": "🖼️ THUMBNAIL", "sub": "📝 SUBTITLE", "doc": "📁 FILE",
"photo": "📸 FOTO", "compress": "🗜️ COMPRESS", "ai": "🤖 CHAT AI",
}
QUALITIES = {"sd": "📺 SD", "hd": "📺 HD", "fhd": "📺 Full HD"}

========================= MENU ==========================

def mode_label(mode):
return MODES.get(mode, mode)

def quality_label(uid):
return QUALITIES.get(user_quality.get(uid, "hd"), "📺 HD")

def main_menu():
return InlineKeyboardMarkup([
[InlineKeyboardButton("🎬 Video", callback_data="mode_video"),
InlineKeyboardButton("🎵 MP3", callback_data="mode_audio")],
[InlineKeyboardButton("🤖 Chat AI", callback_data="mode_ai"),
InlineKeyboardButton("🖼️ Thumbnail", callback_data="mode_thumb")],
[InlineKeyboardButton("📝 Subtitle", callback_data="mode_sub"),
InlineKeyboardButton("📁 File", callback_data="mode_doc")],
[InlineKeyboardButton("📸 Foto", callback_data="mode_photo"),
InlineKeyboardButton("🗜️ Compress", callback_data="mode_compress")],
[InlineKeyboardButton("ℹ️ Info", callback_data="mode_info"),
InlineKeyboardButton("📺 Kualitas", callback_data="quality_menu")],
[InlineKeyboardButton("📊 Statistik", callback_data="stats"),
InlineKeyboardButton("🕘 Riwayat", callback_data="history")],
[InlineKeyboardButton("❓ Bantuan", callback_data="help"),
InlineKeyboardButton("🏓 Cek Bot", callback_data="ping")],
])

def quality_menu():
return InlineKeyboardMarkup([
[InlineKeyboardButton("📺 SD 480p", callback_data="quality_sd")],
[InlineKeyboardButton("📺 HD 720p", callback_data="quality_hd")],
[InlineKeyboardButton("📺 Full HD 1080p", callback_data="quality_fhd")],
[InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")],
])

========================= USER DATA =====================

def add_history(uid, title):
user_history.setdefault(uid, []).insert(0, str(title)[:80])
user_history[uid] = user_history[uid][:MAX_HISTORY]
user_stats[uid] = user_stats.get(uid, 0) + 1

def extract_urls(text):
urls = re.findall(r"https?://[^\s<>]+", text)
return [u.rstrip(".,!?)"]}") for u in urls]

def valid_url(url):
parsed = urlparse(url)
return parsed.scheme in ("http", "https") and bool(parsed.netloc)

========================= AI ===========================

def ai_brain(uid, text):
text = text.strip()
memory = chat_memory.setdefault(uid, [])
memory.append({"role": "user", "content": text})
chat_memory[uid] = memory[-MAX_MEMORY_MESSAGES:]

if GROQ_KEY:  
    try:  
        messages = [{  
            "role": "system",  
            "content": (  
                "Kamu Tiara, asisten AI ramah, lucu, santai, "  
                "berbahasa Indonesia gaul Semarang. Bantu Faris dengan baik."  
            ),  
        }] + chat_memory[uid][-6:]  

        payload = json.dumps({  
            "model": GROQ_MODEL,  
            "messages": messages,  
            "temperature": 0.7,  
            "max_tokens": 500,  
        }).encode("utf-8")  

        request = Request(  
            "https://api.groq.com/openai/v1/chat/completions",  
            data=payload,  
            headers={  
                "Authorization": f"Bearer {GROQ_KEY}",  
                "Content-Type": "application/json",  
            },  
        )  

        with urlopen(request, timeout=25) as response:  
            result = json.loads(response.read().decode("utf-8"))  

        answer = result["choices"][0]["message"]["content"].strip()  
        chat_memory[uid].append({"role": "assistant", "content": answer})  
        chat_memory[uid] = chat_memory[uid][-MAX_MEMORY_MESSAGES:]  
        return answer  
    except Exception as exc:  
        print(f"Groq error: {exc}")  

t = text.lower()  
if any(x in t for x in ["halo", "hai", "hi", "hello", "hey", "pagi", "siang", "malam", "sore"]):  
    return random.choice([  
        "Halo Faris! 👋 Lagi ngapain nih? Mau download atau ngobrol?",  
        "Haiii Faris! 😆 Kirim link atau kita ngobrol aja!",  
        "Halo Faris! Tiara di sini 🤖 Mau download atau cerita?",  
    ])  
if any(x in t for x in ["siapa kamu", "kamu siapa", "nama kamu"]):  
    return "Aku Tiara, bot-nya Faris! 🤖 Bisa download TikTok, Instagram, YouTube, jadi MP3, cek info, HD, plus diajak ngobrol kayak gini!"  
if "siapa faris" in t:  
    return "Faris itu developer yang lagi membangun bot MEGA ini! 😎"  
if any(x in t for x in ["ngantuk", "capek", "lelah", "sedih", "galau"]):  
    return "Waduh, capek ya? Istirahat dulu, Faris. Kalau mau cerita, aku siap mendengarkan. 💛"  
if any(x in t for x in ["lucu", "lawak", "joke", "ngakak"]):  
    return random.choice([  
        "Kenapa TikTok gak pernah tidur? Karena takut ketinggalan FYP! 😂",  
        "Kenapa bot download gak galau? Karena selalu punya file cadangan! 😆",  
    ])  
if any(x in t for x in ["download", "tiktok", "reels", "youtube"]):  
    return "Mau download ya? Pilih mode Video atau MP3, lalu kirim linknya 🎬"  
if any(x in t for x in ["makasih", "thank", "thx", "keren", "mantap", "pinter"]):  
    return "Hehehe, sama-sama Faris! Keren juga kamu terus ngembangin bot ini 😄"  
if "?" in t:  
    return f"Hmm, pertanyaan bagus! Untuk '{text}', aku perlu Groq AI supaya bisa menjawab lebih lengkap."  
return "Aku masih belajar menjawab itu 😅 Aktifkan GROQ_API_KEY agar chat AI lebih pintar."

========================= COMMANDS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
user_mode.setdefault(uid, "video")
user_quality.setdefault(uid, "hd")
name = update.effective_user.first_name or "Faris"

text = (  
    f"Halo {name}! 👋\n\n"  
    "🤖 Bot MEGA + AI - Versi 5.1\n"  
    f"Mode: {mode_label(user_mode[uid])}\n"  
    f"Kualitas: {quality_label(uid)}\n"  
    f"Total Download: {user_stats.get(uid, 0)}\n\n"  
    "FITUR:\n"  
    "🤖 CHAT AI - Ngobrol kayak Tiara!\n"  
    "🎬 Video - TikTok no watermark, Instagram, YT, FB, X\n"  
    "🎵 MP3, 🖼️ Thumbnail, 📝 Subtitle\n"  
    "📁 File, 📸 Foto, 🗜️ Compress, ℹ️ Info\n"  
    "📺 Kualitas SD/HD/Full HD\n"  
    "📦 Batch - Banyak link sekaligus\n"  
    "📊 Statistik + 🕘 Riwayat\n\n"  
    "Cara pakai:\n"  
    "• Download -> pilih mode, kirim LINK\n"  
    "• Ngobrol -> klik 🤖 Chat AI, chat bebas!"  
)  
await update.effective_message.reply_text(text, reply_markup=main_menu())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = (
"📖 CARA PAKAI\n\n"
"🤖 CHAT AI: klik Chat AI lalu chat bebas.\n"
"🎬 DOWNLOAD: pilih mode Video/MP3 dan kirim link.\n\n"
"Perintah: /start /ai /video /mp3 /thumb /sub /doc /photo "
"/compress /info /sd /hd /fhd /stats /history /clear /ping /about /joke /motivasi"
)
await update.effective_message.reply_text(text, reply_markup=main_menu())

async def set_mode_message(update, mode):
uid = update.effective_user.id
user_mode[uid] = mode
message = update.effective_message
if mode == "ai":
text = "🤖 MODE CHAT AI AKTIF!\nChat bebas. Untuk kembali, pilih mode download di menu."
else:
text = f"Mode: {mode_label(mode)} ✅\nKualitas: {quality_label(uid)}\nKirim LINK-nya!"
await message.reply_text(text, reply_markup=main_menu())

async def cmd_quality(update, q):
uid = update.effective_user.id
user_quality[uid] = q
await update.effective_message.reply_text(
f"Kualitas: {quality_label(uid)} ✅", reply_markup=main_menu()
)

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
await update.effective_message.reply_text(
f"📊 Total: {user_stats.get(uid, 0)} | "
f"Mode: {mode_label(user_mode.get(uid, 'video'))} | "
f"Kualitas: {quality_label(uid)}",
reply_markup=main_menu(),
)

async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
history = user_history.get(update.effective_user.id, [])
text = "🕘 RIWAYAT KOSONG" if not history else (
"🕘 RIWAYAT:\n\n" + "\n".join(f"{i}. {title}" for i, title in enumerate(history, 1))
)
await update.effective_message.reply_text(text, reply_markup=main_menu())

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
uid = update.effective_user.id
user_history[uid] = []
chat_memory[uid] = []
await update.effective_message.reply_text(
"Riwayat + memori chat dihapus! 🗑️", reply_markup=main_menu()
)

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.effective_message.reply_text("🏓 PONG! Bot hidup ✅", reply_markup=main_menu())

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.effective_message.reply_text(
"🤖 Bot MEGA + AI v5.1\nDibuat Faris + Tiara ❤️\n"
"Fitur: Chat AI, Video, MP3, Thumbnail, Subtitle, File, Foto, "
"Compress, Info, Kualitas, Batch, Stats, History",
reply_markup=main_menu(),
)

async def cmd_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
answer = await asyncio.to_thread(ai_brain, update.effective_user.id, "ceritain joke dong")
await update.effective_message.reply_text(answer, reply_markup=main_menu())

async def cmd_motivasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.effective_message.reply_text(random.choice([
"🔥 Faris, jangan nyerah! Pelan-pelan, yang penting konsisten.",
"💪 Capek itu wajar. Istirahat sebentar lalu lanjut lagi.",
"✨ Hari ini belajar sedikit pun tetap sebuah kemajuan.",
]), reply_markup=main_menu())

========================= DOWNLOAD =====================

def ytdlp_extract(url, options):
with yt_dlp.YoutubeDL(options) as ydl:
return ydl.extract_info(url, download=not options.get("skip_download", False))

def quality_format(uid):
return {
"sd": "best[height<=480][ext=mp4]/best[height<=480]/best",
"hd": "best[height<=720][ext=mp4]/best[height<=720]/best",
"fhd": "best[height<=1080][ext=mp4]/best[height<=1080]/best",
}.get(user_quality.get(uid, "hd"), "best[height<=720]/best")

async def handle_one(update, context, url, mode):
uid = update.effective_user.id
if not valid_url(url):
await update.effective_message.reply_text("Link tidak valid.")
return

status = await update.effective_message.reply_text(  
    f"⏳ Proses {mode_label(mode)}...\n{url[:100]}"  
)  

try:  
    with tempfile.TemporaryDirectory(prefix="mega_bot_") as temp_dir:  
        output = str(Path(temp_dir) / "%(id)s.%(ext)s")  
        common = {  
            "outtmpl": output,  
            "quiet": True,  
            "noplaylist": True,  
            "max_filesize": MAX_DOWNLOAD_MB * 1024 * 1024,  
            "restrictfilenames": True,  
        }  

        if mode == "info":  
            options = {**common, "skip_download": True}  
            info = await asyncio.to_thread(ytdlp_extract, url, options)  
            text = (  
                f"ℹ️ INFO\n📌 {info.get('title', '-')}\n"  
                f"👤 {info.get('uploader', '-')}\n"  
                f"⏱️ {info.get('duration', 0)} detik\n"  
                f"👀 {info.get('view_count', '-')}\n"  
                f"📅 {info.get('upload_date', '-')}"  
            )  
            await update.effective_message.reply_text(text, reply_markup=main_menu())  
            add_history(uid, info.get("title", "-"))  
            return  

        if mode == "thumb":  
            info = await asyncio.to_thread(  
                ytdlp_extract, url, {**common, "skip_download": True}  
            )  
            thumbnail = info.get("thumbnail")  
            if thumbnail:  
                await update.effective_message.reply_photo(  
                    photo=thumbnail, caption=f"🖼️ {info.get('title', '')[:900]}"  
                )  
                add_history(uid, info.get("title", "-"))  
            else:  
                await update.effective_message.reply_text("Thumbnail tidak tersedia.")  
            return  

        if mode == "sub":  
            options = {  
                **common, "skip_download": True, "writesubtitles": True,  
                "writeautomaticsub": True, "subtitleslangs": ["id", "en"],  
            }  
            info = await asyncio.to_thread(ytdlp_extract, url, options)  
            subtitle_files = list(Path(temp_dir).glob("*.vtt")) + list(Path(temp_dir).glob("*.srt"))  
            if not subtitle_files:  
                await update.effective_message.reply_text("Subtitle tidak tersedia untuk video ini.")  
            else:  
                for file_path in subtitle_files[:3]:  
                    with file_path.open("rb") as file:  
                        await update.effective_message.reply_document(  
                            document=file, filename=file_path.name,  
                            caption=f"📝 Subtitle: {info.get('title', '')[:900]}",  
                        )  
            add_history(uid, info.get("title", "-"))  
            return  

        if mode == "audio":  
            options = {  
                **common, "format": "bestaudio/best",  
                "postprocessors": [{  
                    "key": "FFmpegExtractAudio", "preferredcodec": "mp3",  
                    "preferredquality": "192",  
                }],  
            }  
        elif mode == "compress":  
            options = {**common, "format": "best[height<=480]/best"}  
        else:  
            options = {**common, "format": quality_format(uid)}  

        info = await asyncio.to_thread(ytdlp_extract, url, options)  
        title = str(info.get("title", "Download"))[:100]  
        files = [p for p in Path(temp_dir).iterdir() if p.is_file()]  

        if not files:  
            await update.effective_message.reply_text("File hasil download tidak ditemukan.")  
            return  

        for file_path in files:  
            size_mb = file_path.stat().st_size / (1024 * 1024)  
            if size_mb > MAX_DOWNLOAD_MB:  
                await update.effective_message.reply_text(  
                    f"File {size_mb:.1f} MB terlalu besar untuk batas bot ({MAX_DOWNLOAD_MB} MB)."  
                )  
                continue  

            with file_path.open("rb") as file:  
                if mode == "audio" or file_path.suffix.lower() == ".mp3":  
                    await update.effective_message.reply_audio(  
                        audio=file, title=title, caption=f"🎵 {title}"  
                    )  
                elif mode == "doc":  
                    await update.effective_message.reply_document(  
                        document=file, filename=file_path.name, caption=f"📁 {title}"  
                    )  
                elif mode == "photo" and file_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):  
                    await update.effective_message.reply_photo(photo=file, caption=f"📸 {title}")  
                elif mode == "photo":  
                    await update.effective_message.reply_video(video=file, caption=f"📸 {title}")  
                else:  
                    await update.effective_message.reply_video(  
                        video=file,  
                        caption=f"Berhasil! 🎉\n{title}\nKualitas: {quality_label(uid)}",  
                    )  

        add_history(uid, title)  
        user_mode[uid] = "video"  

except Exception as exc:  
    print(f"Download error: {exc}")  
    await status.edit_text(  
        f"Gagal 😢\n{url[:100]}\nCoba mode SD/Compress.\nError: {str(exc)[:700]}",  
        reply_markup=main_menu(),  
    )  
    return  
finally:  
    try:  
        await status.delete()  
    except Exception:  
        pass

========================= MESSAGE + BUTTONS ============

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
message = update.effective_message
text = (message.text or "").strip()
uid = update.effective_user.id
mode = user_mode.get(uid, "video")
urls = [url for url in extract_urls(text) if valid_url(url)]

if mode == "ai" and not urls:  
    await message.reply_text("🤖 Tiara lagi mikir... ⏳")  
    answer = await asyncio.to_thread(ai_brain, uid, text)  
    await message.reply_text(answer, reply_markup=main_menu())  
    return  

if not urls and mode == "video" and len(text) < 100:  
    answer = await asyncio.to_thread(ai_brain, uid, text)  
    await message.reply_text(answer, reply_markup=main_menu())  
    return  

if not urls:  
    await message.reply_text(  
        "Kirim linknya ya Faris, atau pilih 🤖 Chat AI untuk ngobrol!",  
        reply_markup=main_menu(),  
    )  
    return  

if len(urls) > 1:  
    await message.reply_text(f"📦 Batch: {len(urls[:MAX_BATCH])} link diproses satu per satu.")  

for url in urls[:MAX_BATCH]:  
    await handle_one(update, context, url, mode)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
data = query.data
uid = update.effective_user.id

if data.startswith("mode_"):  
    mode = data.removeprefix("mode_")  
    user_mode[uid] = mode  
    if mode == "ai":  
        text = "🤖 MODE CHAT AI AKTIF!\nChat bebas. Pilih mode download di menu untuk kembali."  
    else:  
        text = f"Mode: {mode_label(mode)} ✅\nKualitas: {quality_label(uid)}\nKirim LINK-nya!"  
    await query.edit_message_text(text, reply_markup=main_menu())  

elif data == "help":  
    await help_cmd(update, context)  
elif data == "quality_menu":  
    await query.edit_message_text(  
        f"📺 PILIH KUALITAS\nSekarang: {quality_label(uid)}",  
        reply_markup=quality_menu(),  
    )  
elif data.startswith("quality_"):  
    q = data.removeprefix("quality_")  
    if q in QUALITIES:  
        user_quality[uid] = q  
    await query.edit_message_text(  
        f"Kualitas: {quality_label(uid)} ✅\nKirim LINK-nya!",  
        reply_markup=main_menu(),  
    )  
elif data == "back_menu":  
    await query.edit_message_text("Menu utama:", reply_markup=main_menu())  
elif data == "ping":  
    await query.edit_message_text("✅ Bot HIDUP!", reply_markup=main_menu())  
elif data == "stats":  
    await query.edit_message_text(  
        f"📊 Total: {user_stats.get(uid, 0)}\n"  
        f"Mode: {mode_label(user_mode.get(uid, 'video'))}\n"  
        f"Kualitas: {quality_label(uid)}",  
        reply_markup
        
    elif data == "stats":
        await query.edit_message_text(
            f"📊 Total: {user_stats.get(uid, 0)}\n"
            f"Mode: {mode_label(user_mode.get(uid, 'video'))}\n"
            f"Kualitas: {quality_label(uid)}",
            reply_markup=main_menu(),
        )

    elif data == "history":
        history = user_history.get(uid, [])
        text = "🕘 RIWAYAT KOSONG" if not history else (
            "🕘 RIWAYAT:\n\n" + "\n".join(
                f"{i}. {t}" for i, t in enumerate(history, 1)
            )
        )
        await query.edit_message_text(text, reply_markup=main_menu())


# ========================= COMMAND ROUTING ==============
async def mode_command(update, context, mode):
    await set_mode_message(update, mode)


def register_mode_command(app, command, mode):
    async def callback(update, context):
        await mode_command(update, context, mode)

    app.add_handler(CommandHandler(command, callback))


def register_quality_command(app, command, quality):
    async def callback(update, context):
        await cmd_quality(update, quality)

    app.add_handler(CommandHandler(command, callback))


# ========================= MAIN ========================
def main():
    if not TOKEN:
        raise RuntimeError("Environment variable TOKEN belum diatur.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))

    for command, mode in [
        ("ai", "ai"), ("chat", "ai"), ("tanya", "ai"),
        ("video", "video"), ("mp3", "audio"), ("thumb", "thumb"),
        ("sub", "sub"), ("doc", "doc"), ("photo", "photo"),
        ("compress", "compress"), ("info", "info"),
    ]:
        register_mode_command(app, command, mode)

    for command, quality in [
        ("sd", "sd"), ("hd", "hd"), ("fhd", "fhd")
    ]:
        register_quality_command(app, command, quality)

    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("about", cmd_about))
    app.add_handler(CommandHandler("joke", cmd_joke))
    app.add_handler(CommandHandler("motivasi", cmd_motivasi))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_message)
    )

    print("Bot MEGA + AI v5.1 berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
