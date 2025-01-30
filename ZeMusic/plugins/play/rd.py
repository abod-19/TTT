from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
from nudenet import NudeDetector

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها (مثال: [-100123456, -100789012])
THRESHOLD = 0.5  # تم تخفيض عتبة الثقة

# تكوين نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.on_message(filters.group & filters.photo)
async def check_image(client, message):
    try:
        # التحقق من المجموعات المسموح بها
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # تنزيل الصورة
        photo = message.photo.file_id
        file_path = await client.download_media(
            photo, 
            file_name=f"temp_{message.id}.jpg",
            in_memory=False
        )
        
        # تحليل الصورة
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
            await asyncio.sleep(1)  # تأخير بسيط قبل الحذف
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"خطأ في معالجة الصورة: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
