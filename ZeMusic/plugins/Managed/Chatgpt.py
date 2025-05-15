import os
import base64
import mimetypes
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from lexica import AsyncClient, languageModels, Messages
from ZeMusic import app
from config import BOT_TOKEN

# متغير لتخزين حالة التفعيل لكل محادثة
activated_chats: dict[int, bool] = {}

# دالة للحصول على المدخل من الرسالة
def get_prompt(message: Message) -> str | None:
    return message.text

# دالة لاستخراج المحتوى من الاستجابة
def extract_content(response) -> str | None:
    content = response.get('content')
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return '\n'.join(item['text'] for item in content if isinstance(item, dict) and 'text' in item)
    elif isinstance(content, dict):
        if 'parts' in content and isinstance(content['parts'], list):
            return '\n'.join(part.get('text', '') for part in content['parts'] if 'text' in part)
        return content.get('text')
    return None

# دالة لتنسيق النص قبل الرد
def format_response(model_name: str, content: str) -> str:
    return f"{content}"

# دالة رئيسية للتعامل مع نماذج النصوص
async def handle_text_model(message: Message, model, model_name: str, as_messages=False):
    prompt = get_prompt(message)
    await message._client.send_chat_action(message.chat.id, ChatAction.TYPING)

    lexica_client = AsyncClient()
    try:
        data = [Messages(content=prompt, role="user")] if as_messages else prompt
        response = await lexica_client.ChatCompletion(data, model)
        content = extract_content(response)
        await message.reply_text(
            format_response(model_name, content) if content else "No content received from the API.",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()

# معالج رسالة لتنفيذ الكود النصي إذا كانت المحادثة مفعلة ويحتوي على نص فقط
@app.on_message(
    filters.private
    & filters.text
    & filters.create(lambda _, __, m: activated_chats.get(m.chat.id, False))
)
async def gpt_handler(client: Client, message: Message):
    if not BOT_TOKEN in ["7026523047:AAG7PYVANPKT2fp2E-itXjbxvDW9R6IHkUQ", "7440472049:AAGA5A57Qj4y4TXCKjvm6PoZXtU3xUHtMDA"]:
        return
    
    # أمر تعطيل داخلي
    if message.text in ["تعطيل", "/de_gpt"]:
        activated_chats[message.chat.id] = False
        await message.reply_text("❌ تم تعطيل البوت في هذه المحادثة.")
        return

    # إذا لم يكن الأمر تعطيل، ننفِّذ النموذج
    await handle_text_model(message, languageModels.gpt, "GPT", as_messages=True)

# أمر تفعيل البوت في المحادثة
@app.on_message(filters.private & filters.command(["تفعيل","en_gpt"], prefixes=["/", ""]))
async def enable_handler(client: Client, message: Message):
    if not BOT_TOKEN in ["7026523047:AAG7PYVANPKT2fp2E-itXjbxvDW9R6IHkUQ", "7440472049:AAGA5A57Qj4y4TXCKjvm6PoZXtU3xUHtMDA","7197234381:AAG4MK3gBEnYBdAj-v13OhdbBxRxggI_Jdk"]:
        return
    activated_chats[message.chat.id] = True
    await message.reply_text("✅ تم تفعيل البوت في هذه المحادثة.")
