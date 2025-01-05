import os
import re
import requests
import sqlite3  # مكتبة SQLite للتعامل مع قاعدة البيانات
import config
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic.platforms.Youtube import cookies
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.database import iffcook, enable_iff, disable_iff


lnk= "https://t.me/" +config.CHANNEL_LINK

# تحديد مسار ثابت لقاعدة البيانات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "songs.db")

# إنشاء أو فتح قاعدة بيانات SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# إنشاء جدول لتخزين المقاطع إذا لم يكن موجوداً
cursor.execute("""
CREATE TABLE IF NOT EXISTS youtube_links (
    video_id TEXT PRIMARY KEY,
    channel_link TEXT
)
""")
conn.commit()

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

@app.on_message(command(["song", "يو", "يوت"]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
        
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    print(f"Database path: {db_path}")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
            return

        video_id = results[0]['id']
        
        # التحقق من وجود المقطع في قاعدة البيانات
        cursor.execute("SELECT channel_link FROM youtube_links WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()
        if row:
            # إذا كان المقطع موجوداً، قم بإرجاع الرابط من قاعدة البيانات
            channel_link = row[0]
            url = f"{channel_link}"
            await client.send_voice(
                chat_id=message.chat.id,
                voice=url,
                caption=f"⟡ {app.mention}",
                reply_to_message_id=message.id,
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
            await m.delete()
            return
        
        # إذا لم يكن موجوداً، أكمل العملية
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
        message_to_channel = await app.send_audio(
            chat_id="@IC_l9",  # إرسال الرسالة إلى القناة
            audio=audio_file,
            caption=f"{results[0]['id']}",
            title=title,
            performer=info_dict.get("uploader", "Unknown"),
            thumb=thumb_name,
            duration=dur,
        )
        
        # حفظ الرابط في قاعدة البيانات
        channel_link = message_to_channel.link
        cursor.execute("INSERT INTO youtube_links (video_id, channel_link) VALUES (?, ?)", (video_id, channel_link))
        conn.commit()

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
                        InlineKeyboardButton(text=config.CHANNEL_NAME, url=channel_link),
                    ],
                ]
            ),
        )
        
        await m.delete()

    except Exception as e:
        await m.edit(f"- لم يتم العثـور على نتائج حاول مجددا\n{str(e)}")
        print(e)

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
