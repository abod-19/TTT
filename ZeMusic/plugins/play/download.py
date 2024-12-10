import random
import glob
import os
import re
import requests
import config
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic import app
from ZeMusic.plugins.play.filters import command

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

def cookies():
    folder_path = f"{os.getcwd()}/cookies"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""

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

    # عرض الصيغ المتاحة
    try:
        ydl_opts = {"listformats": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            formats = info_dict["formats"]
            available_formats = "\n".join(
                [f"{f['format_id']}: {f['ext']} - {f['format_note']}" for f in formats]
            )
            print("Available formats:\n", available_formats)
    except Exception as e:
        await m.edit(f"- حدث خطأ أثناء الحصول على الصيغ المتاحة: {str(e)}")
        print(e)
        return

    # تجربة صيغة مناسبة
    formats_to_try = ["bestaudio/best", "140", "m4a", "mp3"]
    success = False

    for fmt in formats_to_try:
        ydl_opts = {
            "format": fmt,
            "keepvideo": False,
            "geo_bypass": True,
            "outtmpl": f"{title_clean}.%(ext)s",  # استخدام اسم نظيف للملف
            "quiet": True,
            "cookiefile": f"{cookies()}",  # استخدام مسار الكوكيز
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=True)  # التنزيل مباشرة
                audio_file = ydl.prepare_filename(info_dict)
                success = True
                break
        except Exception as e:
            print(f"Format {fmt} failed: {e}")

    if not success:
        await m.edit("- لم يتم العثور على صيغة متوافقة للتنزيل. يرجى مراجعة الصيغ المتاحة.")
        return

    try:
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

    except Exception as e:
        await m.edit(f"- حدث خطأ أثناء إرسال الملف: {str(e)}")
        print(e)

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
