import config
import os
import re
import requests
import yt_dlp
from youtube_search import YoutubeSearch
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ZeMusic.platforms.Youtube import cookies
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.database import iffcook, enable_iff, disable_iff

# وظيفة لحذف الملفات المؤقتة
def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

# رابط القناة والبحث
lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = f"{config.BOT_NAME} ابحث"
Nam = f"{config.BOT_NAME} بحث"

@app.on_message(command(["song", "/song", "بحث", Nem, Nam]))
async def song_downloader(client, message: Message):
    if message.text in ["song", "/song", "بحث", Nem, Nam]:
        return
    elif message.command[0] in config.BOT_NAME:
        query = " ".join(message.command[2:])
    else:
        query = " ".join(message.command[1:])
        
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        title_clean = re.sub(r'[\\/*?:"<>|]', "", title)  # تنظيف اسم الملف
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title_clean}.jpg"
        
        # تحميل الصورة المصغرة
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]

    except Exception as e:
        await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
        print(str(e))
        return
    
    await m.edit("<b>جاري التحميل ♪</b>")

    # إعدادات yt_dlp
    ydl_opts = {
        "format": "best",  # استخدام أفضل صيغة متاحة
        "keepvideo": False,
        "geo_bypass": True,
        "outtmpl": f"{title_clean}.%(ext)s",  # استخدام اسم نظيف للملف
        "quiet": True,
        "cookiefile": f"{await cookies()}",  # استخدام مسار الكوكيز
    }

    try:
        # محاولة تنزيل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)
            
        # حساب مدة الأغنية
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60

        # إرسال الصوت
        await message.reply_audio(
            audio=audio_file,
            caption=f"⟡ {app.mention}",
            title=title,
            performer=info_dict.get("uploader", "Unknown"),
            thumb=thumb_name,
            duration=dur,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=config.CHANNEL_NAME, url=lnk),
                    ],
                ]
            ),
        )
        await m.delete()

    except yt_dlp.utils.DownloadError as e:
        # إذا فشلت الصيغة، جرب صيغة أخرى
        await m.edit(f"- الصيغة المطلوبة غير متاحة. جاري تجربة صيغة بديلة...")
        ydl_opts["format"] = "bestaudio/best"  # تغيير الصيغة إلى خيار آخر
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)
                audio_file = ydl.prepare_filename(info_dict)
        except Exception as e:
            await m.edit(f"- لم يتم العثور على نتائج: {str(e)}")
            return

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
