from ZeMusic import app
import os
from nudenet import NudeDetector
from pyrogram import Client, filters

# تحميل نموذج NudeNet
detector = NudeDetector()

# دالة تحليل الصور
def is_explicit_image(image_path):
    result = detector.detect(image_path)
    for item in result:
        if item["score"] > 0.7:  # إذا كانت نسبة الإباحية أكثر من 70%
            return True
    return False

# استقبال الصور وفحصها
@app.on_message(filters.photo & filters.group)
async def filter_explicit_images(client, message):
    photo = message.photo.file_id  # تصحيح الخطأ هنا
    file_path = await client.download_media(photo)

    if is_explicit_image(file_path):
        await message.delete()
        await message.reply_text("🚫 تم حذف الصورة لأنها غير لائقة!")

    os.remove(file_path)
