import os
import requests
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from ZeMusic import app
from strings.filters import command

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
        # رفع الملف إلى Postimages عبر نموذج الرفع العام
        with open(media, "rb") as f:
            files = {"file": f}
            data = {
                "upload_session": "null",  # بديل لعدم استخدام مفتاح API
                "expiry": "0"  # ترك الصورة بدون انتهاء صلاحية
            }
            headers = {
                "Referer": "https://postimages.org/"
            }
            resp = requests.post("https://postimages.org/json/rr", files=files, data=data, headers=headers)
        
        if resp.status_code == 200:
            json_resp = resp.json()
            upload_url = json_resp.get("image", {}).get("url")  # الرابط المباشر للصورة
            if not upload_url:
                await text.edit_text(f"لم يتم العثور على رابط الصورة في الاستجابة. التفاصيل:\n{resp.text}")
                return
        else:
            await text.edit_text(f"حدث خطأ أثناء الرفع إلى Postimages.\nكود الاستجابة: {resp.status_code}\nالتفاصيل: {resp.text}")
            return
    except Exception as error:
        await text.edit_text(f"استثناء عام أثناء الرفع:\n{error}")
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
