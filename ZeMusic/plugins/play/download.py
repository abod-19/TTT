import os
import re
import aiohttp
import asyncio
import config
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic.platforms.Youtube import cookie_txt_file
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from concurrent.futures import ThreadPoolExecutor

# دالة لحذف الملفات المؤقتة
def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

# دالة للبحث عن فيديو على يوتيوب
async def search_youtube(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            return results[0]
    except Exception as e:
        print(f"Error in search_youtube: {str(e)}")
    return None

# دالة لتحميل الصورة المصغرة باستخدام aiohttp
async def download_thumbnail(url, title):
    try:
        title_clean = re.sub(r'[\\/*?:"<>|]', "", title)  # تنظيف اسم الملف
        thumb_name = f"{title_clean}.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(thumb_name, "wb") as f:
                        f.write(await response.read())
                    return thumb_name
    except Exception as e:
        print(f"Error in download_thumbnail: {str(e)}")
    return None

# دالة لحساب مدة الفيديو بالثواني
def calculate_duration(duration_str):
    secmul, dur, dur_arr = 1, 0, duration_str.split(":")
    for i in range(len(dur_arr) - 1, -1, -1):
        dur += int(float(dur_arr[i])) * secmul
        secmul *= 60
    return dur

# دالة لتنزيل الصوت من يوتيوب في خيط منفصل
async def download_audio(link, title_clean):
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",  # تحديد صيغة M4A
        "keepvideo": False,
        "geo_bypass": True,
        "outtmpl": f"{title_clean}.%(ext)s",  # استخدام اسم نظيف للملف
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info_dict), info_dict

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        try:
            return await loop.run_in_executor(executor, _download)
        except Exception as e:
            print(f"Error in download_audio: {str(e)}")
    return None, None

lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = config.BOT_NAME + " ابحث"

@app.on_message(command(["song", "/song", "بحث", Nem, "تنزيل"]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>⇜ جـارِ البحث ..</b>")
    
    # البحث عن الفيديو
    video_info = await search_youtube(query)
    if not video_info:
        await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
        return

    link = f"https://youtube.com{video_info['url_suffix']}"
    title = video_info["title"][:40]
    thumbnail = video_info["thumbnails"][0]
    duration = video_info["duration"]

    # تحميل الصورة المصغرة
    thumb_name = await download_thumbnail(thumbnail, title)
    if not thumb_name:
        await m.edit("- فشل في تحميل الصورة المصغرة.")
        return

    await m.edit("<b>جاري التحميل ♪</b>")

    # تنزيل الصوت
    audio_file, info_dict = await download_audio(link, title)
    if not audio_file:
        await m.edit(f"error, wait for bot owner to fix\n\nError: Failed to download audio.")
        return

    # حساب مدة الأغنية
    dur = calculate_duration(duration)

    # إرسال الصوت
    try:
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
    except Exception as e:
        await m.edit(f"error, wait for bot owner to fix\n\nError: {str(e)}")
        print(e)

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
