import os
import re
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic import app
from ZeMusic.platforms.Youtube import cookies
from ZeMusic.plugins.play.filters import command

def remove_if_exists(path):
    if path and os.path.exists(path):
        os.remove(path)

@app.on_message(command(["song", "/song", "بحث"]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "keepvideo": False,
        "geo_bypass": True,
        "quiet": True,
        "cookiefile": f"{await cookies()}",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Search and download the audio
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            if not info or 'entries' not in info or not info['entries']:
                await m.edit("لم يتم العثور على نتائج.")
                return
            
            # Get the first result
            first_entry = info['entries'][0]
            title = first_entry.get("title", "Unknown Title")
            lnk = first_entry.get("webpage_url", "Unknown Link")
            thumb_name = first_entry.get("thumbnail", None)
            duration_in_seconds = first_entry.get("duration", 0)
            
            # Clean title and prepare file name
            title_clean = re.sub(r"[^\w\s]", "", title)
            audio_file = ydl.prepare_filename(first_entry).replace('.webm', '.mp3')

            await m.delete()
            await message.reply_audio(
                audio=audio_file,
                caption=f" ⇒ <a href='{lnk}'>{title}</a>\n",
                title=title,
                performer=first_entry.get("uploader", "Unknown"),
                thumb=thumb_name,
                duration=duration_in_seconds,
            )

        except Exception as e:
            await m.edit(f"- لم يتم العثور على نتائج حاول مجددًا\n{str(e)}")
            print(e)

    # Clean up temporary files
    try:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)
    except Exception as e:
        print(e)
