from os import path, remove
import os
from yt_dlp import YoutubeDL
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.formatters import seconds_to_min

class SoundAPI:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "bestaudio/best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "default_search": "ytsearch",
            "quiet": True,
            # حذف الملفات المؤقتة التلقائية
            "keepvideo": False,
            "nopart": True,
        }

    async def search_and_download(self, query: str):
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(f"scsearch:{query}", download=True)
                if not info:
                    return False
                
                track = info["entries"][0]
                file_path = path.join("downloads", f"{track['id']}.{track['ext']}")
                
                duration_sec = int(track.get("duration", 0))
                duration_min = seconds_to_min(duration_sec)
                track_details = {
                    "title": track['title'],
                    "duration_sec": duration_sec,
                    "duration_min": duration_min,
                    "uploader": track.get("uploader", "غير معروف"),
                    "filepath": file_path,
                }
                return track_details, file_path
            except Exception as e:
                print(f"Error: {e}")
                return False

@app.on_message(command(["يوت"]))
async def download_sound(_, message):
    if len(message.command) < 2:
        await message.reply("⚠️ يرجى إدخال اسم المقطع المطلوب!\nمثال: `/يوت اسم الأغنية`")
        return
    
    query = " ".join(message.command[1:])
    sound_api = SoundAPI()
    
    m = await message.reply("⏳ جاري التحميل...")
    result = await sound_api.search_and_download(query)
    
    if not result:
        await m.edit("❌ فشل في العثور على المقطع أو تنزيله!")
        return
    
    track_details, file_path = result
    
    await m.edit(f"""
✅ **تم التحميل بنجاح!**
🏷 **العنوان:** {track_details['title']}
⏳ **المدة:** {track_details['duration_min']}
👤 **الرفع بواسطة:** {track_details['uploader']}
📤 **جاري الإرسال...**
""")
    
    try:
        await message.reply_audio(
            audio=file_path,
            title=track_details["title"],
            performer=track_details["uploader"],
            duration=track_details["duration_sec"]
        )
        await m.delete()
    except Exception as e:
        await message.reply(f"❌ فشل في إرسال الملف!\n```\n{e}\n```")
    finally:
        # حذف الملف سواء نجح الإرسال أو فشل
        try:
            if path.exists(file_path):
                remove(file_path)
                print(f"تم حذف الملف: {file_path}")
            # حذف المجلد إذا كان فارغًا (اختياري)
            downloads_dir = path.dirname(file_path)
            if not os.listdir(downloads_dir):
                os.rmdir(downloads_dir)
        except Exception as delete_error:
            print(f"خطأ في الحذف: {delete_error}")
