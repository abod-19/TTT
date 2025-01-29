import os
from porn-detector import NSFWDetector
from pyrogram import Client, filters
from ZeMusic import app

# تحميل نموذج الكشف عن الصور الإباحية
detector = NSFWDetector()

# دالة تحليل الصور
def is_explicit_image(image_path):
    result = detector.is_nsfw(image_path)
    return result  # إذا كانت الصورة غير لائقة، تُرجع True

# استقبال الصور وفحصها
@app.on_message(filters.photo & filters.group)
async def filter_explicit_images(client, message):
    photo = message.photo[-1]
    file_path = await client.download_media(photo.file_id)

    if is_explicit_image(file_path):
        await message.delete()
        await message.reply_text("🚫 تم حذف الصورة لأنها غير لائقة!")

    os.remove(file_path)
