import os, asyncio
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telegraph import upload_file
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
async def telegraph_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        return await update.reply_text("⌯ ¦ قم بالرد على ملف وسائط مدعوم.\n⌯ ¦ حط صوره او فيديو و اكتب عليها.")
    
    # الحصول على معلومات الملف
    file_info = get_file_id(replied)
    if not file_info:
        return await update.reply_text("⌯ ¦ ياغبي غير مدعوم.\n⌯ ¦ حط صوره و اكتب عليها.")
    
    # رسالة الانتظار
    text = await update.reply_text(text="<code>انتظر يتم التحميل ...</code>", disable_web_page_preview=True)
    
    # تحميل الملف
    media = await update.reply_to_message.download()
    
    # تحقق من نوع media
    print(f"Media type: {type(media)}")  # تحقق مما إذا كان media مسار الملف
    
    await text.edit_text(text="<code>اكتمل التحميل. الآن يتم رفعه إلى التلغراف ...</code>", disable_web_page_preview=True)
    
    try:
        # رفع الملف إلى Telegra.ph
        response = upload_file(media)
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
        text=f"<b>⎉╎الــرابـط : </b><a href='https://telegra.ph{response[0]}'>اضغــط هنـــا</a>\n"
             f"<b>⎉╎مشاركة : </b><a href='https://telegram.me/share/url?url=https://telegra.ph{response[0]}'>اضغــط هنـــا</a>",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="✘ اغلاق ✘", callback_data="close")
        ]])
    )
