import os
import aiohttp
import asyncio
import re
import secrets
import string
import datetime
import time
from pathlib import Path
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from ZeMusic import app

class PostImagCC:
    @staticmethod
    def __get_common_post_data(html: str):
        token = re.findall(r'["\']token["\'].*?[\'"](\w+)["\']', html)
        now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        ui = f'[24,2294,960,"true","","","{now}"]'
        upload_session = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        session_upload = str(time.time() * 1000000)
        
        post_data = {
            "token": token[0],
            "upload_session": upload_session,
            "numfiles": "1",
            "ui": ui,
            "optsize": "0",
            "session_upload": session_upload,
        }
        return post_data

    async def post_file(self, file_path: Path, resp_short: bool = False):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://postimages.org") as resp:
                html = await resp.text()

            data = self.__get_common_post_data(html)
            form = aiohttp.FormData()
            form.add_field("file", file_path.open("rb"))
            for key, value in data.items():
                form.add_field(key, value)
                
            async with session.post("https://postimages.org/json/rr", data=form) as resp:
                res = await resp.json()
                short_url = res["url"]
            return short_url

post_image_service = PostImagCC()

#---------------FUNCTION---------------#

def get_file_id(msg: Message) -> Optional[Message]:
    if not msg.media:
        return None

    for message_type in ("photo", "animation", "audio", "document", "video", "video_note", "voice", "sticker"):
        obj = getattr(msg, message_type)
        if obj:
            setattr(obj, "message_type", message_type)
            return obj

#---------------FUNCTION---------------#

@app.on_message(filters.regex(r"^(تلغراف|ميديا|تلكراف|تلجراف|‹ تلغراف ›)$") & filters.private)
async def cloud_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        return await update.reply_text("⌯ ¦ قم بالرد على ملف وسائط مدعوم.\n⌯ ¦ حط صوره او فيديو و اكتب عليها.")
    
    file_info = get_file_id(replied)
    if not file_info:
        return await update.reply_text("⌯ ¦ ياغبي غير مدعوم.\n⌯ ¦ حط صوره و اكتب عليها.")
    
    text = await update.reply_text(text="<code>انتظر يتم التحميل ...</code>", disable_web_page_preview=True)   
    media = await update.reply_to_message.download()   

    await text.edit_text(text="<code>اكتمل التحميل. الآن يتم رفعه إلى Postimages ...</code>", disable_web_page_preview=True)                                            
    try:
        # رفع الملف إلى Postimages باستخدام الكلاس
        upload_url = await post_image_service.post_file(Path(media))
        
    except Exception as error:
        await text.edit_text(f"حدث خطأ أثناء الرفع:\n{error}")
        return    
    finally:
        try:
            os.remove(media)
        except Exception as error:
            print("خطأ أثناء حذف الملف:", error)

    await text.edit_text(
        text=f"<b>⎉╎الــرابـط :</b> {upload_url}",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton(text="✘ اغلاق ✘", callback_data="close")
        ]])
    )

@app.on_callback_query(filters.regex("close"))
async def close_button(_, query: CallbackQuery):
    await query.message.delete()
