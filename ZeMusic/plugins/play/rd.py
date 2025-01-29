from ZeMusic import app
import os
from nudenet import NudeClassifier
from pyrogram import Client, filters

# تحميل نموذج NudeNet
classifier = NudeClassifier()

# دالة تحليل الصور
def is_explicit_image(image_path):
    result = classifier.classify(image_path)
    for _, data in result.items():
        if data["unsafe"] > 0.7:  # إذا كانت نسبة الإباحية أكثر من 70%
            return True
    return False

# استقبال الصور وفحصها
@app.on_message(filters.photo & filters.group)
async def filter_explicit_images(client, message):
    photo = message.photo[-1]
    file_path = await client.download_media(photo.file_id)

    if is_explicit_image(file_path):
        await message.delete()
        await message.reply_text("🚫 تم حذف الصورة لأنها غير لائقة!")

    os.remove(file_path)
