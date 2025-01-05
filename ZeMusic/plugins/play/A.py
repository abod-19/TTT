from ZeMusic.core.mongo import mongodb
import os
import re
import requests 
import config
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic.platforms.Youtube import cookies
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.database import iffcook, enable_iff, disable_iff

lnk = "https://t.me/" + config.CHANNEL_LINK

songdb = mongodb.song  # مجموعة جديدة لتخزين روابط الفيديوهات

@app.on_message(command(["song", "يو", "يوت"]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
            return

        video_id = results[0]["id"]
        
        # تحقق من وجود المقطع في قاعدة البيانات
        existing_entry = await songdb.find_one({"video_id": video_id})
        if existing_entry:
            channel_link = existing_entry["channel_link"]
            await client.send_voice(
                chat_id=message.chat.id,
                voice=channel_link,
                caption=f"⟡ {app.mention}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=config.CHANNEL_NAME, url=lnk)]]
                ),
                reply_to_message_id=message.id,
            )
            await m.delete()
            return
        
        # تحميل المقطع من يوتيوب
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        title_clean = re.sub(r'[\\/*?:"<>|]', "", title)
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

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "geo_bypass": True,
        "outtmpl": f"{title_clean}.%(ext)s",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)

        # إرسال الصوت إلى القناة
        message_to_channel = await app.send_audio(
            chat_id="@IC_l9",
            audio=audio_file,
            caption=f"{results[0]['id']}",
            title=title,
            performer=info_dict.get("uploader", "Unknown"),
            thumb=thumb_name,
        )
        
        # حفظ الرابط في قاعدة البيانات
        channel_link = message_to_channel.link
        await songdb.insert_one({"video_id": video_id, "channel_link": channel_link})

        # إرسال الصوت إلى المستخدم
        await message.reply_audio(
            audio=audio_file,
            caption=f"⟡ {app.mention}",
            title=title,
            performer=info_dict.get("uploader", "Unknown"),
            thumb=thumb_name,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=config.CHANNEL_NAME, url=channel_link)]]
            ),
        )
        
        await m.delete()

    except Exception as e:
        await m.edit(f"- حدث خطأ أثناء التحميل:\n{str(e)}")
        print(e)

    # حذف الملفات المؤقتة
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)
