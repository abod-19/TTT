import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
from ZeMusic import app
from ZeMusic.plugins.play.filters import command

lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = f"{config.BOT_NAME} ابحث"
Nam = f"{config.BOT_NAME} بحث"

def remove_if_exists(path):
    """حذف الملفات المؤقتة إذا كانت موجودة"""
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"خطأ أثناء حذف الملف {path}: {str(e)}")

@app.on_message(command(["song", "/song", "بحث", Nem, Nam]))
async def song_downloader(client, message: Message):
    if message.text in ["song", "/song", "بحث", Nem, Nam]:
        return
    elif message.command[0] in config.BOT_NAME:
        query = " ".join(message.command[2:])
    else:
        query = " ".join(message.command[1:])
    
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")

    # البحث عن رابط الأغنية في SoundCloud
    try:
        data = requests.get(f"https://m.soundcloud.com/search?q={query}")
        urls = re.findall(r'data-testid="cell-entity-link" href="([^"]+)', data.text)
        names = re.findall(r'<div class="Information_CellTitle__2KitR">([^<]+)', data.text)

        result = []
        for i in range(len(urls)):
            result.append({'name': names[i], 'url': f'{urls[i]}'})

        buttons = []
        count = 0
        for a in result:
            if count == 5:
                break
            url = a['url']
            buttons.append([
                InlineKeyboardButton(a['name'], switch_inline_query_current_chat=f'{url}#SOUND')
            ])
            count += 1

        btns = InlineKeyboardMarkup(buttons)
        await m.edit(f"<b>نتائج البحث لـ {query}:</b>", reply_markup=btns)

    except Exception as e:
        await m.edit(f"⚠️ حدث خطأ أثناء معالجة الطلب: {str(e)}")
        print(f"Error: {e}")
