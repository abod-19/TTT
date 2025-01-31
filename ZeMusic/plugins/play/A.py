from os import path
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
            # إضافة خيارات البحث في SoundCloud
            "default_search": "ytsearch",
            "quiet": True,
        }

    async def search_and_download(self, query: str):
        # البحث والتنزيل باستخدام الاستعلام
        with YoutubeDL(self.opts) as ydl:
            try:
                info = ydl.extract_info(f"scsearch:{query}", download=True)
                if not info:
                    return False
                # الحصول على أول نتيجة
                track = info["entries"][0]
                xyz = path.join("downloads", f"{track['id']}.{track['ext']}")
                duration_min = seconds_to_min(track["duration"])
                track_details = {
                    "title": track["title"],
                    "duration_sec": track["duration"],
                    "duration_min": duration_min,
                    "uploader": track["uploader"],
                    "filepath": xyz,
                }
                return track_details, xyz
            except Exception as e:
                print(f"Error: {e}")
                return False

@app.on_message(command(["يوت"]))
async def download_sound(_, message):
    # التحقق من وجود استعلام
    if len(message.command) < 2:
        await message.reply("⚠️ يرجى إدخال اسم المقطع المطلوب!\nمثال: `/يوت اسم الأغنية`")
        return
    
    query = " ".join(message.command[1:])
    sound_api = SoundAPI()
    
    # إرسال رسالة تفيد بأن التنزيل بدأ
    m = await message.reply("⏳ جاري التحميل...")
    
    # البحث والتنزيل
    result = await sound_api.search_and_download(query)
    
    if not result:
        await m.edit("❌ فشل في العثور على المقطع أو تنزيله!")
        return
    
    track_details, file_path = result
    # إرسال التفاصيل بعد التنزيل
    await m.edit(f"""
✅ **تم التحميل بنجاح!**
🏷 **العنوان:** {track_details['title']}
⏳ **المدة:** {track_details['duration_min']}
👤 **الرفع بواسطة:** {track_details['uploader']}
📁 **المسار:** `{file_path}`
""")
