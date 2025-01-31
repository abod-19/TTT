from os import path
from yt_dlp import YoutubeDL
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.formatters import seconds_to_min

class SoundAPI:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "bestaudio[ext=m4a]",  # تحميل بصيغة M4A
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
            "default_search": "ytsearch",
            "quiet": True,
        }

    async def search_and_download(self, query: str):
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(f"scsearch:{query}", download=True)
                if not info:
                    return False
                
                track = info["entries"][0]
                file_path = path.join("downloads", f"{track['id']}.m4a")  # تحديد المسار
                
                duration_min = seconds_to_min(track["duration"])
                track_details = {
                    "title": track["title"],
                    "duration_sec": track["duration"],
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
    
    # إرسال الملف الصوتي مباشرةً
    try:
        await message.reply_audio(
            audio=file_path,
            title=track_details["title"],
            performer=track_details["uploader"],
            duration=track_details["duration_sec"]
        )
        await m.delete()  # حذف رسالة "جاري الإرسال..."
    except Exception as e:
        await message.reply(f"❌ فشل في إرسال الملف!\n```\n{e}\n```")
