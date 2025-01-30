import os
import asyncio
from pyrogram import Client
from pytube import YouTube
from youtubesearchpython import VideosSearch
from ZeMusic import app
from ZeMusic.plugins.play.filters import command

@app.on_message(command(["song", "/song", "بحث"]))
async def pytube_downloader(client, message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>⚡ جـارِ البحث السريع...</b>")

    try:
        # البحث الفوري بدون كوكيز
        search = VideosSearch(query, limit=1)
        result = search.result()
        if not result['result']:
            return await m.edit("⚠️ لم يتم العثور على نتائج")

        video_url = result['result'][0]['link']
        
        # التحميل المباشر
        yt = YouTube(video_url)
        stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
        
        await m.edit("<b>🚀 جـارِ التحميل الفائق...</b>")
        download_path = await asyncio.to_thread(stream.download, output_path="downloads")
        
        # التحويل السريع إلى MP3
        base = os.path.splitext(download_path)[0]
        audio_file = base + '.mp3'
        os.rename(download_path, audio_file)

        # الإرسال مع معالجة مسبقة
        await message.reply_chat_action("upload_audio")
        await m.edit("<b>📤 جـاري التحميل إلى التليجرام...</b>")
        await message.reply_audio(
            audio=audio_file,
            caption=f"🎵 {yt.title[:50]}",
            duration=yt.length,
            performer=yt.author[:30],
            thumb=yt.thumbnail_url,
            file_name=yt.title[:30] + ".mp3"
        )

    except Exception as e:
        await m.edit(f"❌ خطأ: {str(e)[:100]}")
    finally:
        # تنظيف الملفات المؤقتة
        if 'audio_file' in locals():
            try:
                os.remove(audio_file)
            except:
                pass
