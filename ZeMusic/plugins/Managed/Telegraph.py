import os
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from imgurpython import ImgurClient
from ZeMusic import app

# إعدادات API لـ Imgur (استبدل هذه القيم بالقيم الخاصة بك من Imgur)
CLIENT_ID = "a7655efe0d76c1c"
CLIENT_SECRET = "358c318228ef4abd45e5b5787920bf0b41eb2633"

# إعداد اتصال Imgur
imgur_client = ImgurClient(CLIENT_ID, CLIENT_SECRET)

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
async def imgur_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        return await update.reply_text("⌯ ¦ قم بالرد على صورة مدعومة.\n⌯ ¦ حط صوره و اكتب عليها.")
    
    file_info = get_file_id(replied)
    if not file_info:
        return await update.reply_text("⌯ ¦ ياغبي غير مدعوم.\n⌯ ¦ حط صوره و اكتب عليها.")
    
    text = await update.reply_text(text="<code>انتظر يتم التحميل ...</code>", disable_web_page_preview=True)
    
    media = await update.reply_to_message.download()
    await text.edit_text(text="<code>اكتمل التحميل. الآن يتم رفعه إلى Imgur ...</code>", disable_web_page_preview=True)
    
    try:
        # رفع الصورة إلى Imgur
        response = imgur_client.upload_from_path(media, anon=True)
        imgur_url = response['link']  # تأكد من أن هذا هو المفتاح الصحيح
    except Exception as error:
        print(error)
        await text.edit_text(text=f"Error :- {error}", disable_web_page_preview=True)
        return
    
    try:
        # حذف الملف المحلي بعد الرفع
        os.remove(media)
    except Exception as error:
        print(error)
        return
    
    # تعديل الرسالة وإضافة الروابط
    await text.edit_text(
        text=f"<b>⎉╎الــرابـط : </b><a href='{imgur_url}'>اضغــط هنـــا</a>\n"
             f"<b>⎉╎مشاركة : </b><a href='https://telegram.me/share/url?url={imgur_url}'>اضغــط هنـــا</a>",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="✘ اغلاق ✘", callback_data="close")
        ]])
    )
