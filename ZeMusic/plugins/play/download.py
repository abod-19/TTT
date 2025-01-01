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

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)
W = [0]
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
        channel_id = "IC_l9"  # استبدل هذا بمعرف القناة الخاص بك
        search_text = results[0]['id']
        async for msg in client.search_messages(chat_id=channel_id, query=search_text):
            if msg.voice:  # تحقق إذا كانت الرسالة تحتوي على مقطع صوتي
                # إرسال المقطع الصوتي إلى نفس الدردشة
                await client.send_voice(
                    chat_id=message.chat.id,  # إرسال المقطع الصوتي إلى دردشة المستخدم
                    voice=msg.voice.file_id,  # الملف الصوتي الموجود في الرسالة
                    caption="🤍",  # تعليق مع المقطع الصوتي
                    reply_to_message_id=message.id,  # الرد على الرسالة الأصلية
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=config.CHANNEL_NAME, url=lnk
                                )
                            ],
                        ]
                    )
                )
            return  # إنهاء العملية بعد العثور على المقطع الصوتي

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

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",  # تحديد صيغة M4A
        "keepvideo": False,
        "geo_bypass": True,
        "outtmpl": f"{title_clean}.%(ext)s",  # استخدام اسم نظيف للملف
        "quiet": True,
        "cookiefile": f"{await cookies()}",  # استخدام مسار الكوكيز
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)  # التنزيل مباشرة
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

        await app.send_audio(
            chat_id="@IC_l9",  # إرسال الرسالة إلى القناة
            audio=audio_file,
            caption=f"{results[0]['id']}",
            title=title,
            performer=info_dict.get("uploader", "Unknown"),
            thumb=thumb_name,
            duration=dur,
        )
        
        await m.delete()

    except Exception as e:
        await m.edit(f"- لم يتم العثـور على نتائج حاول مجددا")
        global W
        if "ERROR: [youtube]" in str(e):
            W[0] += 1
            if W[0] >= 3:
                W = [0]
                if await iffcook():
                    await disable_iff()
                else:
                    await enable_iff()
        try:
            dev_id = 5145609515
            usr = await c.get_users(dev_id)
            usrnam = usr.username
            await app.send_message(
                chat_id=f"@{usrnam}",
                text=f"<p>{await iffcook()}\t{W}</p>\n{str(e)}"
            )
        except Exception as x:
            print(x) 
        print(e)

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
