from ZeMusic import app
from pyrogram import filters  # أضفنا استيراد الفلاتر من Pyrogram
import os
import logging
from nudenet import NudeDetector

# التهيئة والإعدادات
detector = NudeDetector()
ALLOWED_GROUPS = []  
THRESHOLD = 0.7  

# تكوين نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.on_message(filters.group & filters.photo)  # أصبحت الفلاتر معروفة الآن
async def check_image(client, message):
    try:
        # التحقق من المجموعات المسموح بها
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # تنزيل الصورة
        photo = message.photo.file_id
        file_path = await client.download_media(photo, file_name=f"temp_{message.id}.jpg")
        
        # تحليل الصورة
        results = detector.detect(file_path)
        
        # التحقق من النتائج
        inappropriate_detected = False
        for obj in results:
            if obj['class'] in [
                'FEMALE_GENITALIA_COVERED', 
                'BUTTOCKS_EXPOSED',
                'FEMALE_BREAST_EXPOSED', 
                'MALE_GENITALIA_EXPOSED'
            ] and obj['score'] >= THRESHOLD:
                inappropriate_detected = True
                break
        
        if inappropriate_detected:
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")
        
        # تنظيف الملفات
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"خطأ: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
