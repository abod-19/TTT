import os
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic import app

@app.on_message(filters.private | filters.group)
async def handle_media(client: Client, message: Message):
    if message.photo:
        # إذا كانت الرسالة تحتوي على صورة
        file_info = await client.download_media(message.photo, file_name="temp_image")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام صورة بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.video:
        # إذا كانت الرسالة تحتوي على فيديو
        file_info = await client.download_media(message.video, file_name="temp_video")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام فيديو بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.document:
        # إذا كانت الرسالة تحتوي على ملف
        file_info = await client.download_media(message.document, file_name="temp_file")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام ملف بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.audio:
        # إذا كانت الرسالة تحتوي على ملف صوتي
        file_info = await client.download_media(message.audio, file_name="temp_audio")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام ملف صوتي بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.voice:
        # إذا كانت الرسالة تحتوي على تسجيل صوتي
        file_info = await client.download_media(message.voice, file_name="temp_voice")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام تسجيل صوتي بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.sticker:
        # إذا كانت الرسالة تحتوي على ملصق
        file_info = await client.download_media(message.sticker, file_name="temp_sticker")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام ملصق بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    elif message.animation:
        # إذا كانت الرسالة تحتوي على رسوم متحركة (GIF)
        file_info = await client.download_media(message.animation, file_name="temp_animation")
        file_extension = os.path.splitext(file_info)[1].lower()
        await message.reply_text(f"تم استلام رسوم متحركة بنوع: {file_extension}")
        os.remove(file_info)  # حذف الملف المؤقت بعد الانتهاء منه

    else:
        # إذا كانت الرسالة نصية أو غير معروفة
        await message.reply_text("تم استلام رسالة نصية أو نوع غير معروف.")
