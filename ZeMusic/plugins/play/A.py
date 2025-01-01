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

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)
W = [0]
lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = f"{config.BOT_NAME} ابحث"
Nam = f"{config.BOT_NAME} بحث"

@app.on_message(command(["song", "يوت", "يو", Nem, Nam]))
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
        channel_id = "IC_l9"  # استبدل هذا بمعرف القناة الخاص بك
        search_text = results[0]['id']
        async for msg in client.search_messages(chat_id=channel_id, query=search_text):
            if msg.voice:  # تحقق إذا كانت الرسالة تحتوي على مقطع صوتي
                # إرسال المقطع الصوتي إلى نفس الدردشة
                await client.send_voice(
                    chat_id=message.chat.id,  # إرسال المقطع الصوتي إلى دردشة المستخدم
                    voice=msg.voice.file_id,  # الملف الصوتي الموجود في الرسالة
                    caption="🤍",  # تعليق مع المقطع الصوتي
                    reply_to_message_id=message.id,  # الرد على الرسالة الأصلية
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text=config.CHANNEL_NAME, url=lnk
                                )
                            ],
                        ]
                    )
                )
            return  # إنهاء العملية بعد العثور على المقطع الصوتي

    await message.reply("لم يتم العثور على أي مقاطع صوتية تحتوي على النص المطلوب.")
