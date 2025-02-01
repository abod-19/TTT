import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
from openai import OpenAI

# تهيئة عميل OpenAI
client_openai = OpenAI(api_key="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")

@app.on_message(command(["رسم"]))
async def generate_image(client: Client, message: Message):
    try:
        # استخراج النص بعد الأمر
        description = " ".join(message.command[1:])
        
        if not description:
            await message.reply_text("❗ يرجى كتابة وصف للصورة بعد الأمر /رسم")
            return
            
        # إرسال طلب توليد الصورة
        response = client_openai.images.generate(
            model="dall-e-3",
            prompt=description,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # تنزيل الصورة
        image_response = requests.get(image_url)
        image_path = f"temp_image_{message.id}.png"
        
        with open(image_path, "wb") as f:
            f.write(image_response.content)
        
        # إرسال الصورة
        await message.reply_photo(
            photo=image_path,
            caption=f"تم إنشاء الصورة بناء على الوصف:\n`{description}`"
        )
        
        # تنظيف الملف المؤقت
        os.remove(image_path)
        
    except Exception as e:
        await message.reply_text(f"❌ فشل في إنشاء الصورة: {str(e)}")
