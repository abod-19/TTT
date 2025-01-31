from os import path, remove, makedirs
import os
import requests
from yt_dlp import YoutubeDL
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.formatters import seconds_to_min
import config

lnk = "https://t.me/" + config.CHANNEL_LINK

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
            "keepvideo": False,
            "nopart": True,
            "writethumbnail": True,  # تفعيل حفظ الصورة المصغرة
        }

    async def search_and_download(self, query: str):
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(f"scsearch:{query}", download=True)
                if not info:
                    return False
                
                track = info["entries"][0]
                file_path = path.join("downloads", f"{track['id']}.{track['ext']}")
                
                # تنزيل الصورة المصغرة
                thumbnail_url = track.get("thumbnail")
                thumbnail_path = None
                if thumbnail_url:
                    thumbnail_path = self.download_thumbnail(track['id'], thumbnail_url)
                
                duration_sec = int(track.get("duration", 0))
                duration_min = seconds_to_min(duration_sec)
                track_details = {
                    "title": track['title'],
                    "duration_sec": duration_sec,
                    "duration_min": duration_min,
                    "uploader": track.get("uploader", "غير معروف"),
                    "filepath": file_path,
                    "thumbnail": thumbnail_path,
                }
                return track_details, file_path
            except Exception as e:
                print(f"Error: {e}")
                return False

    def download_thumbnail(self, track_id: str, url: str):
        try:
            makedirs("thumbnails", exist_ok=True)
            thumbnail_path = f"thumbnails/{track_id}.jpg"
            response = requests.get(url)
            with open(thumbnail_path, "wb") as f:
                f.write(response.content)
            return thumbnail_path
        except Exception as e:
            print(f"فشل في تنزيل الصورة: {e}")
            return None

@app.on_message(command(["ساوند"]))
async def download_sound(_, message):
    if len(message.command) < 2:
        return
    
    query = " ".join(message.command[1:])
    sound_api = SoundAPI()
    
    m = await message.reply("- جـارِ البحث ♪.")
    result = await sound_api.search_and_download(query)
    
    if not result:
        await m.edit("- فشل في العثور على المقطع.")
        return
    
    track_details, file_path = result    
    await m.edit(f"- جـارِ التحميل ♪.")
    
    try:
        await message.reply_audio(
            audio=file_path,
            caption=f"<p>- </p><a href='{lnk}'>{app.name}</a>\nㅤ",
            title=track_details["title"],
            performer=track_details["uploader"],
            duration=track_details["duration_sec"],
            thumb=track_details["thumbnail"] or None,  # إضافة الصورة هنا
        )
        await m.delete()
    except Exception as e:
        await message.reply(f"- فشل في إرسال الملف.")
        print(e)
    finally:
        
        # حذف الملفات المؤقتة
        try:
            if path.exists(file_path):
                remove(file_path)
            if track_details["thumbnail"] and path.exists(track_details["thumbnail"]):
                remove(track_details["thumbnail"])
        except Exception as delete_error:
            print(f"خطأ في الحذف: {delete_error}")
