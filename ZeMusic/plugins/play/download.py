import os
import asyncio
import random
from pytube import YouTube
from youtubesearchpython import VideosSearch
from pyrogram import Client
from ZeMusic import app
from ZeMusic.plugins.play.filters import command

# إعدادات التحميل الآمن
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
]

def setup_pytube():
    """تهيئة pytube مع إعدادات مخصصة"""
    from pytube import request
    request.default_range_size = 1048576  # 1MB chunks
    request.timeout = 10

def get_yt_object(video_url):
    """إنشاء كائن YouTube بشكل آمن"""
    yt = YouTube(
        video_url,
        use_oauth=False,
        allow_oauth_cache=False
    )
    
    # إضافة headers إذا لم تكن موجودة
    if not hasattr(yt, '_author') or not hasattr(yt._author, 'headers'):
        yt._author = type('obj', (object,), {'headers': {}})()
        yt._author.headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    return yt

@app.on_message(command(["song", "/song", "بحث"]))
async def ultimate_downloader(client, message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>🔍 جـارِ البحث الآمن...</b>")

    try:
        # البحث مع إعدادات مخصصة
        search = VideosSearch(query, limit=1)
        result = search.result()
        if not result['result']:
            return await m.edit("⚠️ لم يتم العثور على نتائج")

        video_url = result['result'][0]['link']
        
        # تهيئة pytube
        setup_pytube()
        
        # إنشاء كائن YouTube بشكل آمن
        yt = get_yt_object(video_url)
        
        # اختيار أفضل تنسيق صوتي
        stream = yt.streams.filter(
            only_audio=True,
            file_extension='mp4'
        ).order_by('abr').desc().first()
        
        if not stream:
            return await m.edit("❌ لم يتم العثور على تنسيق صوتي مناسب")

        await m.edit("<b>🚀 جـارِ التحميل الآمن...</b>")
        download_path = await asyncio.to_thread(
            stream.download,
            output_path="downloads",
            skip_existing=False,
            timeout=10
        )
        
        # التحويل إلى MP3
        base = os.path.splitext(download_path)[0]
        audio_file = base + '.mp3'
        os.rename(download_path, audio_file)

        # الإرسال
        await message.reply_chat_action("upload_audio")
        await m.edit("<b>📤 جـاري الإرسال الآمن...</b>")
        await message.reply_audio(
            audio=audio_file,
            caption=f"🎵 {yt.title[:50]}",
            duration=yt.length,
            performer=yt.author[:30],
            thumb=yt.thumbnail_url,
            file_name=yt.title[:30] + ".mp3"
        )

    except Exception as e:
        await m.edit(f"❌ خطأ آمن: {str(e)[:100]}")
    finally:
        if 'audio_file' in locals():
            try:
                os.remove(audio_file)
            except:
                pass
