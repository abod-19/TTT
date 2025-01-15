"""
import os
import re
import requests
import config
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from ZeMusic.platforms.Youtube import cookies
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.database import iffcook, enable_iff, disable_iff
from ZeMusic.core.mongo import mongodb

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

songdb = mongodb.song
lnk = "https://t.me/" + config.CHANNEL_LINK

@app.on_message(command(["يو", "/song", "يوت"]))
async def song_downloader(client, message: Message):
    query = " ".join(message.command[1:])
        
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("- لم يتم العثـور على نتائج حاول مجددا")
            return

        video_id = results[0]['id']
        try:
            # تحقق من وجود المقطع في قاعدة البيانات
            existing_entry = await songdb.find_one({"video_id": video_id})
            if existing_entry:
                channel_link = existing_entry["channel_link"]
                await client.send_voice(
                    chat_id=message.chat.id,
                    voice=channel_link,
                    caption=f" ⇒ <a href='{lnk}'>{app.name}</a>\nㅤ",
                    reply_to_message_id=message.id,
                )
                await m.delete()
                return
        except Exception as q:
            print(str(q))

    except Exception as e:
        await m.edit(f"- لم يتم العثـور على نتائج حاول مجددا") 
        print(e)
"""
