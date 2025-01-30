from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
import aiofiles
from nudenet import NudeDetector

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها
THRESHOLD = 0.45  # تم تخفيض العتبة

# تكوين نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.on_message(filters.group & (filters.photo | filters.video))
async def check_media(client, message):
    try:
        # التحقق من المجموعات المسموح بها
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # تنزيل الملف
        if message.photo:
            media = message.photo.file_id
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            media = message.video.file_id
            file_path = f"temp_{message.id}.mp4"
        
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(await client.download_media(media))
        
        # تحليل الملف
        results = detector.detect(file_path)
        logger.info(f"نتائج التحليل: {results}")
        
        # التحقق من النتائج
        inappropriate_detected = False
        for obj in results:
            if obj['class'] in [
                'EXPOSED_ANUS',
                'COVERED_GENITALIA',
                'EXPOSED_GENITALIA',
                'FEMALE_GENITALIA_COVERED', 
                'BUTTOCKS_EXPOSED',
                'FEMALE_BREAST_EXPOSED', 
                'MALE_GENITALIA_EXPOSED'
            ] and obj['score'] >= THRESHOLD:
                inappropriate_detected = True
                logger.info(f"تم الكشف عن: {obj['class']} بثقة {obj['score']}")
                break
        
        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذف الصورة خلال 10 ثوانٍ.")
            await asyncio.sleep(10)  # تأخير 10 ثوانٍ
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
