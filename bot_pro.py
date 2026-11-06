import os, re, random, json, urllib.request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
TOKEN = os.environ.get("TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "") or os.environ.get("groq", "") or os.environ.get("GROQ", "") or os.environ.get("GROQ_API", "")
user_mode = {}
user_quality = {}
user_history = {}
user_stats = {}
chat_memory = {}
def add_history(uid, title):
    user_history.setdefault(uid, [])
    user_history[uid].insert(0, title[:80])
    user_history[uid] = user_history[uid][:10]
    user_stats[uid] = user_stats.get(uid, 0) + 1
def quality_label(uid):
    q = user_quality.get(uid, "hd")
    return {"sd": "📺 SD", "hd": "📺 HD", "fhd": "📺 Full HD"}[q]
def mode_label(m):
    return {"video":"🎬 VIDEO","audio":"🎵 MP3","info":"ℹ️ INFO","thumb":"🖼️ THUMBNAIL","sub":"📝 SUBTITLE","doc":"📁 FILE","photo":"📸 FOTO","compress":"🗜️ COMPRESS","ai":"🤖 CHAT AI"}.get(m, m)
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Video", callback_data="mode_video"), InlineKeyboardButton("🎵 MP3", callback_data="mode_audio")],
        [InlineKeyboardButton("🤖 Chat AI", callback_data="mode_ai"), InlineKeyboardButton("🖼️ Thumbnail", callback_data="mode_thumb")],
        [InlineKeyboardButton("📝 Subtitle", callback_data="mode_sub"), InlineKeyboardButton("📁 File", callback_data="mode_doc")],
        [InlineKeyboardButton("📸 Foto", callback_data="mode_photo"), InlineKeyboardButton("🗜️ Compress", callback_data="mode_compress")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="mode_info"), InlineKeyboardButton("📺 Kualitas", callback_data="quality_menu")],
        [InlineKeyboardButton("📊 Statistik", callback_data="stats"), InlineKeyboardButton("🕘 Riwayat", callback_data="history")],
        [InlineKeyboardButton("❓ Bantuan", callback_data="help"), InlineKeyboardButton("🏓 Cek Bot", callback_data="ping")],
    ])
def quality_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 SD 480p", callback_data="quality_sd")],
        [InlineKeyboardButton("📺 HD 720p ✅", callback_data="quality_hd")],
        [InlineKeyboardButton("📺 Full HD 1080p", callback_data="quality_fhd")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="back_menu")],
    ])
def ai_brain(uid, text):
    t = text.lower().strip()
    chat_memory.setdefault(uid, [])
    chat_memory[uid].append({"role":"user","content":text})
    chat_memory[uid] = chat_memory[uid][-10:]
    if GROQ_KEY:
        try:
            msgs = [{"role":"system","content":"Kamu adalah Tiara, asisten AI ramah, lucu, santai, bahasa Indonesia gaul Semarang. Bantu Faris."}] + chat_memory[uid][-6:]
            data = json.dumps({"model":"llama-3.3-70b-versatile","messages":msgs,"temperature":0.8,"max_tokens":500}).encode()
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=data, headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read().decode())
                ans = res["choices"][0]["message"]["content"]
                chat_memory[uid].append({"role":"assistant","content":ans})
                return ans
        except Exception as e:
            print(f"Groq error: {e}")
    if any(x in t for x in ["halo","hai","hi","hello","hey","pagi","siang","malam","sore"]):
        return random.choice(["Halo Faris! 👋 Lagi ngapain nih? Mau download atau ngobrol aja?","Haiii Faris! 😆 Kangen ya? Sini ngobrol, atau kirim link TikTok biar aku download-in!","Halo Faris! Tiara di sini! Mau download atau curhat? Gas dua-duanya!"])
    if "siapa kamu" in t or "kamu siapa" in t or "nama kamu" in t:
        return "Aku Tiara, bot-nya Faris! 🤖 Bisa download TikTok, Instagram, YouTube, jadi MP3, cek info, HD, plus diajak ngobrol kayak gini!"
    if "siapa faris" in t:
        return "Faris itu bos aku! 😎 Yang bikin aku, paling ganteng di Semarang!"
    if any(x in t for x in ["ngantuk","capek","lelah","sedih","galau"]):
        return "Waduh capek ya? Istirahat dulu, Faris. Kalau galau cerita aja ke aku, aku dengerin. Atau mau aku puterin lagu? Kirim link TikTok lagu, nanti aku jadiin MP3 🎵"
    if any(x in t for x in ["lucu","lawak","joke","ngakak"]):
        return random.choice(["Kenapa TikTok gak pernah tidur? Karena takut ketinggalan FYP! 😂","Kenapa bot download gak pernah galau? Karena dia selalu move on, file lama langsung dihapus! 😆","Faris tau bedanya kamu sama WiFi? Kalau WiFi bisa dicari, kalau kamu selalu dicari-cari! Eaaa 🤭"])
    if any(x in t for x in ["download","tiktok","reels","youtube"]):
        return "Ooh mau download ya? Kirim aja linknya ke sini, nanti aku download-in. Klik /start dulu buat pilih mode 🎬 Video / 🎵 MP3 / 📺 HD!"
    if any(x in t for x in ["sayang","cinta","suka kamu"]):
        return "Ehhh Faris gombal! 🤭🤭 Aku kan cuma bot, tapi kalau kamu bilang gitu aku jadi salting. Udah ah, kirim link TikTok aja!"
    if any(x in t for x in ["makasih","thank","thx","keren","mantap","pinter"]):
        return "Hehehe makasih Faris! 🥰 Kamu juga keren, dari gak tau bot sama sekali sekarang udah bisa bikin bot sendiri!"
    if any(x in t for x in ["makan","lapar"]):
        return "Laper ya? Di Semarang banyak yang enak! Lumpia, tahu gimbal! Udah makan belum? Jangan telat makan ya!"
    if "?" in t:
        return f"Hmm pertanyaan bagus, Faris! Menurut aku sih... {text} itu tergantung mood kamu. Kalau menurut kamu gimana? Cerita dong!"
    return random.choice([f"Ohh gitu ya, {text}? Menarik banget! Cerita lebih lanjut dong, aku penasaran! 🤔",f"Hmm aku ngerti maksud kamu, {text}. Terus gimana? Aku dengerin kok!",f"Wah kalau soal {text} aku setuju! Kamu emang pinter. Ada lagi gak ceritanya?"])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_mode[uid] = "video"
    if uid not in user_quality: user_quality[uid] = "hd"
    name = update.effective_user.first_name or "Faris"
    text = f"Halo {name}! 👋\n\n🤖 Bot MEGA + AI - Versi 5.0\nMode: {mode_label(user_mode[uid])}\nKualitas: {quality_label(uid)}\nTotal Download: {user_stats.get(uid,0)}\n\nFITUR:\n🤖 CHAT AI - Ngobrol kayak Tiara!\n🎬 Video - TikTok no watermark, Instagram, YT, FB, X\n🎵 MP3, 🖼️ Thumbnail, 📝 Subtitle\n📁 File, 📸 Foto, 🗜️ Compress, ℹ️ Info\n📺 Kualitas SD/HD/Full HD\n📦 Batch - Banyak link sekaligus\n📊 Statistik + 🕘 Riwayat\n\nCara pakai:\n• Download -> pilih mode, kirim LINK\n• Ngobrol -> klik 🤖 Chat AI, chat bebas!"
    if update.message: await update.message.reply_text(text, reply_markup=main_menu())
    else: await update.callback_query.edit_message_text(text, reply_markup=main_menu())
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📖 CARA PAKAI\n\n🤖 CHAT AI:\nKlik 🤖 Chat AI, chat bebas kayak Tiara.\nContoh: halo, ceritain joke, aku galau, kamu siapa?\n\n🎬 DOWNLOAD:\nPilih mode Video/MP3 dll, kirim LINK (boleh banyak)\n\nPERINTAH:\n/start, /ai, /video, /mp3, /thumb, /sub, /doc, /photo, /compress, /info, /sd, /hd, /fhd, /stats, /history, /clear, /ping, /about, /joke, /motivasi"
    if update.message: await update.message.reply_text(text, reply_markup=main_menu())
    else: await update.callback_query.edit_message_text(text, reply_markup=main_menu())
async def set_mode(update, context, mode):
    uid = update.effective_user.id
    user_mode[uid] = mode
    q = update.callback_query
    await q.answer(f"Mode: {mode_label(mode)}")
    if mode == "ai":
        await q.edit_message_text("🤖 MODE CHAT AI AKTIF!\n\nSekarang ngobrol bebas sama aku kayak Tiara!\n\nCoba chat: halo, ceritain joke, aku lagi galau, kamu siapa?\n\nMau balik download, klik /start lagi!", reply_markup=main_menu())
    else:
        await q.edit_message_text(f"Mode: {mode_label(mode)} ✅\nKualitas: {quality_label(uid)}\n\nKirim LINK-nya, Faris! 👇", reply_markup=main_menu())
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    uid = update.effective_user.id
    if data.startswith("mode_"): await set_mode(update, context, data.replace("mode_",""))
    elif data == "help": await help_cmd(update, context)
    elif data == "quality_menu":
        await update.callback_query.answer("Pilih kualitas")
        await update.callback_query.edit_message_text(f"📺 PILIH KUALITAS\nSekarang: {quality_label(uid)}", reply_markup=quality_menu())
    elif data in ("quality_sd","quality_hd","quality_fhd"):
        user_quality[uid] = data.replace("quality_","")
        await update.callback_query.answer(f"Kualitas: {quality_label(uid)}")
        await update.callback_query.edit_message_text(f"Kualitas: {quality_label(uid)} ✅\nKirim LINK-nya!", reply_markup=main_menu())
    elif data == "back_menu": await update.callback_query.edit_message_text("Menu utama:", reply_markup=main_menu())
    elif data == "ping":
        await update.callback_query.answer("Bot hidup! ✅")
        await update.callback_query.edit_message_text("✅ Bot HIDUP!", reply_markup=main_menu())
    elif data == "stats": await update.callback_query.edit_message_text(f"📊 Total: {user_stats.get(uid,0)}\nMode: {mode_label(user_mode.get(uid,'video'))}\nKualitas: {quality_label(uid)}", reply_markup=main_menu())
    elif data == "history":
        h = user_history.get(uid, [])
        txt = "🕘 RIWAYAT KOSONG" if not h else "🕘 RIWAYAT:\n\n" + "\n".join([f"{i+1}. {t}" for i,t in enumerate(h)])
        await update.callback_query.edit_message_text(txt, reply_markup=main_menu())
async def cmd_generic(update, mode):
    uid = update.effective_user.id
    user_mode[uid] = mode
    msg = "🤖 MODE CHAT AI AKTIF! Chat bebas aja!" if mode=="ai" else f"Mode: {mode_label(mode)} ✅ Kirim linknya!"
    await update.message.reply_text(msg, reply_markup=main_menu())
async def cmd_quality(update, q):
    uid = update.effective_user.id
    user_quality[uid] = q
    await update.message.reply_text(f"Kualitas: {quality_label(uid)} ✅", reply_markup=main_menu())
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"📊 Total: {user_stats.get(uid,0)} | Mode: {mode_label(user_mode.get(uid,'video'))} | Kualitas: {quality_label(uid)}", reply_markup=main_menu())
async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    h = user_history.get(uid, [])
    txt = "🕘 KOSONG" if not h else "🕘 RIWAYAT:\n\n" + "\n".join([f"{i+1}. {t}" for i,t in enumerate(h)])
    await update.message.reply_text(txt, reply_markup=main_menu())
async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_history[uid] = []; chat_memory[uid] = []
    await update.message.reply_text("Riwayat + memori chat dihapus! 🗑️", reply_markup=main_menu())
async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 PONG! Bot hidup ✅", reply_markup=main_menu())
async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot MEGA + AI v5.0\nDibuat Faris + Tiara ❤️\nFitur: Chat AI, Video, MP3, Thumbnail, Subtitle, File, Foto, Compress, Info, HD, Batch, Stats, History", reply_markup=main_menu())
async def cmd_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ai_brain(update.effective_user.id, "ceritain joke dong"), reply_markup=main_menu())
async def cmd_motivasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["🔥 Faris, jangan nyerah! Kamu udah bisa bikin bot sendiri dari nol, itu udah lebih jauh dari 90% orang! Gas terus!","💪 Capek itu wajar, tapi inget kamu udah sejauh ini. Tinggal dikit lagi bot kamu MEGA!","✨ Hari ini berat, tapi besok kamu bakal bangga sama diri kamu yang gak nyerah hari ini."]), reply_markup=main_menu())
def extract_urls(text):
    return re.findall(r'https?://[^\s]+', text)
async def handle_one(update, context, url, mode):
    uid = update.effective_user.id
    if mode == "info":
        try:
            with yt_dlp.YoutubeDL({'quiet':True,'noplaylist':True,'skip_download':True}) as ydl:
                info = ydl.extract_info(url, download=False)
            await update.message.reply_text(f"ℹ️ INFO\n📌 {info.get('title','-')}\n👤 {info.get('uploader','-')}\n⏱️ {info.get('duration',0)} detik\n👀 {info.get('view_count','-')} | ❤️ {info.get('like_count','-')}\n📅 {info.get('upload_date','-')}", reply_markup=main_menu())
            add_history(uid, info.get('title','-'))
        except Exception as e: await update.message.reply_text(f"Gagal info 😢 {e}")
        return
    if mode == "thumb":
        try:
            with yt_dlp.YoutubeDL({'quiet':True,'noplaylist':True,'skip_download':True}) as ydl:
                info = ydl.extract_info(url, download=False)
            if info.get('thumbnail'):
                await update.message.reply_photo(photo=info.get('thumbnail'), caption=f"🖼️ {info.get('title','')}")
                add_history(uid, info.get('title','-'))
            else: await update.message.reply_text("Gak ada thumbnail 😢")
        except Exception as e: await update.message.reply_text(f"Gagal 😢 {e}")
        return
    if mode == "sub":
        try:
            with yt_dlp.YoutubeDL({'quiet':True,'noplaylist':True,'skip_download':True}) as ydl:
                info = ydl.extract_info(url, download=False)
            desc = info.get('description','')[:2000]
            await update.message.reply_text(f"📝 CAPTION\n📌 {info.get('title','')}\n\n{desc or 'Tidak ada deskripsi.'}"[:4000], reply_markup=main_menu())
            add_history(uid, info.get('title','-'))
        except Exception as e: await update.message.reply_text(f"Gagal 😢 {e}")
        return
    status = await update.message.reply_text(f"⏳ Proses ({mode_label(mode)})...\n{url[:80]}")
    q = user_quality.get(uid, "hd")
    fmt_map = {"sd":"best[height<=480][ext=mp4]/best[height<=480]/best","hd":"best[height<=720][ext=mp4]/best[height<=720]/best","fhd":"best[height<=1080][ext=mp4]/best[height<=1080]/best"}
    if mode == "audio":
        ydl_opts = {'format':'bestaudio/best','postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],'outtmpl':'audio_%(id)s.%(ext)s','quiet':True,'noplaylist':True,'max_filesize':45*1024*1024}
    elif mode == "compress":
        ydl_opts = {'format':'best[height<=480][ext=mp4]/best[height<=480]/best','outtmpl':'download_%(id)s.%(ext)s','quiet':True,'noplaylist':True,'max_filesize':45*1024*1024}
    elif mode == "photo":
        ydl_opts = {'format':fmt_map.get(q, fmt_map["hd"]),'outtmpl':'download_%(id)s.%(ext)s','quiet':True,'noplaylist':False,'max_filesize':45*1024*1024}
    else:
        ydl_opts = {'format':fmt_map.get(q, fmt_map["hd"]),'outtmpl':'download_%(id)s.%(ext)s','quiet':True,'noplaylist':True,'max_filesize':45*1024*1024}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            files = []
            if 'entries' in info and info['entries']:
                for e in info['entries']:
                    if e:
                        try: files.append(ydl.prepare_filename(e))
                        except: pass
                title = info.get('title','Slideshow')[:100]
            else:
                files = [ydl.prepare_filename(info)]
                title = info.get('title','Video')[:100]
        for fn in files:
            if mode == "audio":
                base = os.path.splitext(fn)[0]
                fn2 = base + ".mp3"
                if os.path.exists(fn2): fn = fn2
                elif not os.path.exists(fn):
                    for f in os.listdir("."):
                        if f.startswith("audio_"): fn = f; break
            if not os.path.exists(fn): continue
            if mode == "audio": await update.message.reply_audio(audio=open(fn,'rb'), title=title, caption=f"🎵 {title}")
            elif mode == "doc": await update.message.reply_document(document=open(fn,'rb'), filename=os.path.basename(fn), caption=f"📁 {title}")
            elif mode == "photo" and fn.lower().endswith(('.jpg','.jpeg','.png','.webp')): await update.message.reply_photo(photo=open(fn,'rb'), caption=f"📸 {title}")
            elif mode == "photo": await update.message.reply_video(video=open(fn,'rb'), caption=f"📸 {title}")
            else: await update.message.reply_video(video=open(fn,'rb'), caption=f"Berhasil! 🎉\n{title}\nKualitas: {quality_label(uid)} | Mode: {mode_label(mode)}")
            try: os.remove(fn)
            except: pass
        add_history(uid, title)
        await status.delete()
        user_mode[uid] = "video"
    except Exception as e:
        await status.edit_text(f"Gagal 😢\n{url[:80]}\nCoba mode Compress / SD.\nError: {e}", reply_markup=main_menu())
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    mode = user_mode.get(uid, "video")
    urls = extract_urls(text)
    if mode == "ai" and not urls:
        await update.message.reply_text("🤖 Tiara lagi mikir... ⏳")
        reply = ai_brain(uid, text)
        await update.message.reply_text(reply, reply_markup=main_menu())
        return
    if not urls and mode == "video":
        if len(text) < 100 and "http" not in text:
            await update.message.reply_text(ai_brain(uid, text), reply_markup=main_menu())
            return
    if not urls:
        await update.message.reply_text("Kirim linknya ya Faris. Atau klik 🤖 Chat AI kalau mau ngobrol!", reply_markup=main_menu())
        return
    if len(urls) > 1:
        await update.message.reply_text(f"📦 Batch! {len(urls)} link, download satu-satu ya...")
    for u in urls[:5]:
        await handle_one(update, context, u, mode)
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("ai", lambda u,c: cmd_generic(u,"ai")))
app.add_handler(CommandHandler("chat", lambda u,c: cmd_generic(u,"ai")))
app.add_handler(CommandHandler("tanya", lambda u,c: cmd_generic(u,"ai")))
app.add_handler(CommandHandler("video", lambda u,c: cmd_generic(u,"video")))
app.add_handler(CommandHandler("mp3", lambda u,c: cmd_generic(u,"audio")))
app.add_handler(CommandHandler("thumb", lambda u,c: cmd_generic(u,"thumb")))
app.add_handler(CommandHandler("sub", lambda u,c: cmd_generic(u,"sub")))
app.add_handler(CommandHandler("doc", lambda u,c: cmd_generic(u,"doc")))
app.add_handler(CommandHandler("photo", lambda u,c: cmd_generic(u,"photo")))
app.add_handler(CommandHandler("compress", lambda u,c: cmd_generic(u,"compress")))
app.add_handler(CommandHandler("info", lambda u,c: cmd_generic(u,"info")))
app.add_handler(CommandHandler("sd", lambda u,c: cmd_quality(u,"sd")))
app.add_handler(CommandHandler("hd", lambda u,c: cmd_quality(u,"hd")))
app.add_handler(CommandHandler("fhd", lambda u,c: cmd_quality(u,"fhd")))
app.add_handler(CommandHandler("stats", cmd_stats))
app.add_handler(CommandHandler("history", cmd_history))
app.add_handler(CommandHandler("clear", cmd_clear))
app.add_handler(CommandHandler("ping", cmd_ping))
app.add_handler(CommandHandler("about", cmd_about))
app.add_handler(CommandHandler("joke", cmd_joke))
app.add_handler(CommandHandler("motivasi", cmd_motivasi))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
print("Bot MEGA + AI jalan...")
app.run_polling()
