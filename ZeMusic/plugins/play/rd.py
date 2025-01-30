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
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها هنا
THRESHOLD = 0.35  # عتبة اكتشاف المحتوى غير اللائق
FRAME_INTERVAL = 0.5  # تحليل إطار كل 0.5 ثانية في الفيديو

# تكوين نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.on_message(filters.group & (filters.photo | filters.video | filters.sticker | filters.animation))
async def check_media(client, message):
    try:
        # التحقق من المجموعات المسموح بها
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # تحديد نوع الملف
        file_path = None
        if message.photo:
            media = message.photo.file_id
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            media = message.video.file_id
            file_path = f"temp_{message.id}.mp4"
        elif message.sticker:
            media = message.sticker.file_id
            file_path = f"temp_{message.id}.webp"
        elif message.animation:  # الملصقات المتحركة (GIFs)
            media = message.animation.file_id
            file_path = f"temp_{message.id}.mp4"
        else:
            return

        # تنزيل الملف
        media_bytes_io = await client.download_media(media, in_memory=True)

        if not media_bytes_io or not media_bytes_io.getvalue():
            logger.error("فشل تنزيل الملف أو الملف فارغ!")
            return

        # حفظ الملف محليًا
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(media_bytes_io.getvalue())

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.error(f"فشل في حفظ الملف: {file_path} غير موجود أو فارغ")
            return

        # تحليل الملف
        inappropriate_detected = False

        if message.photo or message.sticker or message.animation:
            results = detector.detect(file_path) if os.path.exists(file_path) else []
            for obj in results:
                if obj['class'] in [
                    'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
                    'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
                    'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                    'FEMALE_GENITALIA_EXPOSED'
                ] and obj['score'] >= THRESHOLD:
                    inappropriate_detected = True
                    logger.info(f"تم الكشف عن محتوى غير لائق: {obj['class']} بثقة {obj['score']}")
                    break

        elif message.video:
            try:
                clip = VideoFileClip(file_path)
                duration = clip.duration  
            except Exception as e:
                logger.error(f"فشل فتح الفيديو {file_path}: {str(e)}")
                return

            for t in np.arange(0, duration, FRAME_INTERVAL):
                frame_path = f"temp_frame_{message.id}_{int(t)}.jpg"

                try:
                    clip.save_frame(frame_path, t=t)
                except Exception as e:
                    logger.error(f"فشل استخراج الإطار عند {t} ثانية: {str(e)}")
                    continue

                if os.path.exists(frame_path) and os.path.getsize(frame_path) > 0:
                    results = detector.detect(frame_path)
                    for obj in results:
                        if obj['class'] in [
                            'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
                            'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
                            'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                            'FEMALE_GENITALIA_EXPOSED'
                        ] and obj['score'] >= THRESHOLD:
                            inappropriate_detected = True
                            logger.info(f"تم الكشف عن محتوى غير لائق في الإطار عند {t:.2f} ثانية")
                            break

                os.remove(frame_path) if os.path.exists(frame_path) else None

                if inappropriate_detected:
                    break

            clip.close()  

        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذفه خلال 5 ثوانٍ.")
            await asyncio.sleep(5)
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")

        # حذف الملفات المؤقتة
        os.remove(file_path) if os.path.exists(file_path) else None

    except Exception as e:
        logger.error(f"خطأ أثناء معالجة الملف: {str(e)}")

    finally:
        # التأكد من تنظيف الملفات المؤقتة حتى في حالة حدوث خطأ
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
