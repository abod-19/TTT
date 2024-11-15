import os
import re
import aiohttp
import aiofiles
from yt_dlp import YoutubeDL
from youtubesearchpython.__future__ import VideosSearch
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ZeMusic import app
from ZeMusic.plugins.play.filters import command
import config


# إزالة الملف إذا كان موجودًا
def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


# إعداد OAuth مع yt_dlp
ytdl = YoutubeDL({
    "format": "bestaudio/best",
    "outtmpl": "cache/%(id)s.%(ext)s",
    "username": "oauth2",
    "password": "",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "320",
    }],
})

CHANNEL_LINK = f"https://t.me/{config.CHANNEL_LINK}"
BOT_NAME = config.BOT_NAME


@app.on_message(command(["song", "/song", "بحث", f"{BOT_NAME} ابحث", "يوت"]) & filters.group)
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
    msg = await message.reply_text("<b>⇜ جـارِ البحث ..</b>")

    try:
        # البحث عن الأغنية
        search = VideosSearch(query, limit=1)
        results = (await search.next())["result"]
        if not results:
            await msg.edit("- لم يتم العثور على نتائج. حاول مجددًا.")
            return

        video = results[0]
        link = video["link"]
        title = video["title"]
        title_clean = re.sub(r'[\\/*?:"<>|]', "", title)  # تنظيف اسم الملف
        thumbnail_url = video["thumbnails"][0]["url"]
        duration = video["duration"]

        # تنزيل الصورة المصغرة
        thumb_name = f"cache/{title_clean}.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(thumb_name, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        await msg.edit("<b>⇜ جـارِ التنزيل ..</b>")

        # تنزيل الصوت باستخدام yt_dlp
        audio_file = None
        try:
            ytdl.download([link])
            audio_file = f"cache/{title_clean}.mp3"  # تحديد مسار الملف الذي سيتم تنزيله
            await msg.edit("<b>⇜ جاري التحميل ♫ ..</b>")

        except Exception as e:
            await msg.edit(f"- حدث خطأ أثناء التنزيل: {str(e)}")
            print(e)
            return

        # حساب مدة الأغنية
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60

        # إرسال الصوت إلى المستخدم مع البيانات الوصفية
        try:
            await message.reply_audio(
                audio=audio_file,
                caption=f"⟡ {app.mention}",
                title=title,
                performer=video["channel"]["name"],
                thumb=thumb_name,
                duration=dur,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=config.CHANNEL_NAME, url=CHANNEL_LINK),
                        ],
                    ]
                ),
            )

            # حذف الملفات المؤقتة بعد إرسال الصوت
            remove_if_exists(audio_file)
            remove_if_exists(thumb_name)

            # حذف الرسالة التي تحتوي على حالة التحميل
            await msg.delete()

        except Exception as e:
            await msg.edit(f"- حدث خطأ أثناء إرسال الصوت: {str(e)}")
            print(e)
            remove_if_exists(audio_file)
            remove_if_exists(thumb_name)

    except Exception as e:
        await msg.edit("- حدث خطأ أثناء البحث: حاول مجددًا.")
        print(str(e))
