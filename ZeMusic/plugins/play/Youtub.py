from os import path, remove, makedirs
import os
from yt_dlp import YoutubeDL
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.formatters import seconds_to_min
import config

lnk = "https://t.me/" + config.CHANNEL_LINK

class Youtube:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "bestaudio/best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "default_search": "ytsearch",
            "quiet": True,
            "keepvideo": False,
            "nopart": True,
            "writethumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                },
                {"key": "EmbedThumbnail"},
            ],
        }

    async def search_and_download(self, query: str):
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)
                if not info:
                    return False
                
                track = info["entries"][0]
                file_path = ydl.prepare_filename(track).replace(".webm", ".mp3")
                thumbnail_path = f"downloads/{track['id']}.webp"
                
                duration_sec = int(track.get("duration", 0))
                duration_min = seconds_to_min(duration_sec)
                
                track_details = {
                    "title": track['title'],
                    "duration_sec": duration_sec,
                    "duration_min": duration_min,
                    "uploader": track.get('uploader', 'Unknown Channel'),
                    "filepath": file_path,
                    "thumbnail": thumbnail_path if path.exists(thumbnail_path) else None,
                }
                return track_details, file_path
            except Exception as e:
                print(f"Error: {e}")
                return False

@app.on_message(command(["يوت"]))
async def download_youtube(_, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ يرجى إدخال اسم المقطع المطلوب!")
    
    query = " ".join(message.command[1:])
    yt_api = Youtube()
    
    m = await message.reply("🔎 جـارِ البحث...")
    result = await yt_api.search_and_download(query)
    
    if not result:
        return await m.edit("❌ لم يتم العثور على النتيجة!")
    
    track_details, file_path = result    
    await m.edit("⬇️ جـارِ التحميل...")
    
    try:
        await message.reply_audio(
            audio=file_path,
            #caption=f"<b>➲ العنوان:</b> {track_details['title']}\n<b>➲ القناة:</b> {track_details['uploader']}\n\n{lnk}",
            title=track_details["title"],
            performer=track_details["uploader"],
            duration=track_details["duration_sec"],
            thumb=track_details["thumbnail"],
        )
    except Exception as e:
        await message.reply("❌ فشل في إرسال الملف!")
        print(e)
    finally:
        await m.delete()
        # تنظيف الملفات المؤقتة
        for file in [file_path, track_details["thumbnail"]]:
            try:
                if file and path.exists(file):
                    remove(file)
            except Exception as delete_error:
                print(f"خطأ في الحذف: {delete_error}")
