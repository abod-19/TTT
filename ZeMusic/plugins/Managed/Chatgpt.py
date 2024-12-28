import requests
from BadAPI import api
from pyrogram import filters
from pyrogram.enums import ChatAction
from ZeMusic import app

@app.on_message(
    filters.command(["رون"], "")
)
async def gemini_handler(client, message):
    # عرض مؤشر الكتابة
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)

    # استخراج المدخلات من المستخدم
    if (
        message.text.startswith(f"/gemini@{app.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text("كيف يمكنني مساعدتك اليوم؟")
            return

    # محاولة معالجة المدخلات والحصول على النتائج
    try:
        response = api.gemini(user_input)
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)

        # التحقق من صحة الاستجابة
        if response and isinstance(response, dict) and "results" in response:
            x = response["results"]
            if x:
                await message.reply_text(x, quote=True)
            else:
                await message.reply_text("حدث خطأ: النتائج فارغة.")
        else:
            await message.reply_text("حدث خطأ: الاستجابة غير صحيحة.")
    
    # معالجة أخطاء الطلب
    except requests.exceptions.RequestException as e:
        await message.reply_text(f"حدث خطأ في الطلب: {e}")
    
    # معالجة أي أخطاء غير متوقعة
    except Exception as e:
        await message.reply_text(f"خطأ غير متوقع: {e}")
