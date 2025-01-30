from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
import aiofiles
import numpy as np
from nudenet import NudeDetector
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image  # استيراد مكتبة Pillow للتعامل مع الصور

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # أضف أيدي المجموعات المسموح بها
THRESHOLD = 0.35  # تم تخفيض العتبة
FRAME_INTERVAL = 1.0  # تحليل إطار كل 1 ثانية لتحسين الأداء

# تكوين نظام التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def convert_webp_to_png(webp_path, png_path):
    """تحويل ملف webp إلى png باستخدام Pillow"""
    try:
        with Image.open(webp_path) as img:
            img.save(png_path, "PNG")
        return True
    except Exception as e:
        logger.error(f"فشل تحويل {webp_path} إلى {png_path}: {str(e)}")
        return False

@app.on_message(filters.group & (filters.photo | filters.video | filters.sticker | filters.animation))
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
        elif message.sticker:
            media = message.sticker.file_id
            file_path = f"temp_{message.id}.webp"  # الملصقات تكون بصيغة webp
        elif message.animation:  # GIFs
            media = message.animation.file_id
            file_path = f"temp_{message.id}.mp4"  # GIFs يتم تحميلها كفيديو
        else:
            return

        # تنزيل الملف ككائن BytesIO
        media_bytes_io = await client.download_media(media, in_memory=True)

        # تحقق من نجاح التنزيل
        if not media_bytes_io:
            logger.error("فشل تنزيل الملف: media_bytes_io هو None")
            return

        media_data = media_bytes_io.getvalue()

        # تحقق مما إذا كانت البيانات فارغة
        if not media_data:
            logger.error("الملف الذي تم تنزيله فارغ!")
            return

        # كتابة البيانات في ملف
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(media_data)

        # تأكد من أن الملف تم إنشاؤه
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.error(f"فشل في حفظ الملف: {file_path} غير موجود أو فارغ")
            return

        # تحليل الملف
        inappropriate_detected = False

        if message.photo or message.animation:
            # تحليل الصور والصور المتحركة
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                results = detector.detect(file_path)
            else:
                logger.error(f"الملف {file_path} غير موجود أو فارغ، لا يمكن تحليله")
                return

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

        elif message.sticker:
            # تحويل الملصق من webp إلى png
            png_path = f"temp_{message.id}.png"
            if await convert_webp_to_png(file_path, png_path):
                if os.path.exists(png_path) and os.path.getsize(png_path) > 0:
                    results = detector.detect(png_path)
                else:
                    logger.error(f"الملف {png_path} غير موجود أو فارغ، لا يمكن تحليله")
                    return

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

                # تنظيف الملف المؤقت
                if os.path.exists(png_path):
                    os.remove(png_path)

        elif message.video:
            # تحليل الفيديو (استخراج عدة إطارات)
            try:
                with VideoFileClip(file_path) as clip:
                    duration = clip.duration  # مدة الفيديو بالثواني

                    for t in np.arange(0, duration, FRAME_INTERVAL):  # تحليل إطار كل FRAME_INTERVAL ثانية
                        frame_path = f"temp_frame_{message.id}_{int(t)}.jpg"

                        try:
                            clip.save_frame(frame_path, t=t)
                        except Exception as e:
                            logger.error(f"فشل استخراج الإطار عند {t} ثانية: {str(e)}")
                            continue

                        if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
                            logger.warning(f"الإطار عند {t} ثانية غير صالح.")
                            continue

                        results = detector.detect(frame_path)

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

            except Exception as e:
                logger.error(f"فشل فتح الفيديو {file_path}: {str(e)}")
                return

        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذف الملف خلال 5 ثوانٍ.")
            await asyncio.sleep(5)  # تأخير 5 ثوانٍ
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")

    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {str(e)}")
    finally:
        # التأكد من حذف الملفات المؤقتة حتى في حالة حدوث خطأ
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
