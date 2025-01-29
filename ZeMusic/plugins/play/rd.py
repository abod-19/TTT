from ZeMusic import app
import os
import logging
from nudenet import NudeDetector

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها (مثال: [-100123456, -100789012])
THRESHOLD = 0.7  # عتبة الثقة للكشف

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
        file_path = await client.download_media(photo, file_name=f"temp_{message.id}.jpg")
        
        # تحليل الصورة
        results = detector.detect(file_path)
        
        # التحقق من النتائج
        for obj in results:
            if obj['class'] in [
                'FEMALE_GENITALIA_COVERED', 
                'BUTTOCKS_EXPOSED',
                'FEMALE_BREAST_EXPOSED', 
                'MALE_GENITALIA_EXPOSED'
            ] and obj['score'] >= THRESHOLD:
                
                # حذف الرسالة إذا تم اكتشاف محتوى غير لائق
                await message.delete()
                logger.info(f"تم حذف رسالة غير لائقة في المجموعة {message.chat.id}")
                break
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"خطأ في معالجة الصورة: {e}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
