from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
import aiofiles
import numpy as np
from nudenet import NudeDetector
from moviepy.video.io.VideoFileClip import VideoFileClip

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها
THRESHOLD = 0.35  # تم تخفيض العتبة
FRAME_INTERVAL = 0.5  # تحليل إطار كل 0.5 ثانية

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

        # تحديد نوع الملف
        if message.photo:
            media = message.photo.file_id
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            media = message.video.file_id
            file_path = f"temp_{message.id}.mp4"
        else:
            return

        # تنزيل الملف ككائن BytesIO
        media_bytes_io = await client.download_media(media, in_memory=True)

        # تحويل BytesIO إلى bytes
        media_data = media_bytes_io.getvalue()

        # كتابة البيانات في ملف
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(media_data)

        # تحليل الملف
        inappropriate_detected = False

        if message.photo:
            # تحليل الصورة
            results = detector.detect(file_path)
            logger.info(f"نتائج تحليل الصورة: {results}")

            for obj in results:
                if obj['class'] in [
                    'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
                    'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
                    'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                    'FEMALE_GENITALIA_EXPOSED'
                ] and obj['score'] >= THRESHOLD:
                    inappropriate_detected = True
                    logger.info(f"تم الكشف عن: {obj['class']} بثقة {obj['score']}")
                    break

        elif message.video:
            # تحليل الفيديو (استخراج عدة إطارات)
            clip = VideoFileClip(file_path)
            duration = clip.duration  # مدة الفيديو بالثواني

            for t in np.arange(0, duration, FRAME_INTERVAL):  # تحليل إطار كل FRAME_INTERVAL ثانية
                frame_path = f"temp_frame_{message.id}_{int(t)}.jpg"
                clip.save_frame(frame_path, t=t)  # حفظ الإطار كصورة

                # تحليل الإطار
                results = detector.detect(frame_path)
                logger.info(f"نتائج تحليل إطار الفيديو (الوقت: {t:.2f} ثانية): {results}")

                for obj in results:
                    if obj['class'] in [
                        'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
                        'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
                        'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                        'FEMALE_GENITALIA_EXPOSED'
                    ] and obj['score'] >= THRESHOLD:
                        inappropriate_detected = True
                        logger.info(f"تم الكشف عن: {obj['class']} بثقة {obj['score']} في الإطار (الوقت: {t:.2f} ثانية)")
                        break

                # تنظيف الإطار المؤقت
                if os.path.exists(frame_path):
                    os.remove(frame_path)

                if inappropriate_detected:
                    break  # إيقاف التحليل إذا تم اكتشاف محتوى غير لائق

            clip.close()  # إغلاق الفيديو لتحرير الموارد

        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذف الملف خلال 5 ثوانٍ.")
            await asyncio.sleep(5)  # تأخير 5 ثوانٍ
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")

        # تنظيف الملفات المؤقتة
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {str(e)}")
    finally:
        # التأكد من حذف الملفات المؤقتة حتى في حالة حدوث خطأ
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
