from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
import subprocess
from nudenet import NudeDetector
from moviepy.video.io.VideoFileClip import VideoFileClip

# تهيئة كاشف المحتوى غير اللائق
detector = NudeDetector()

# إعدادات البوت
ALLOWED_GROUPS = []  # ضع معرفات المجموعات المسموح بها هنا
THRESHOLD = 0.35  # الحد الأدنى لاكتشاف المحتوى غير اللائق
FRAME_INTERVAL = 0.5  # تحليل إطار كل 0.5 ثانية من الفيديو

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

        file_path = None
        converted_video = None

        if message.photo:
            media = message.photo.file_id
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            media = message.video.file_id
            file_path = f"temp_{message.id}.mp4"
        elif message.sticker:  # تحويل الملصقات إلى فيديو
            media = message.sticker.file_id
            sticker_path = f"temp_{message.id}.webp"
            
            # إعادة المحاولة حتى 3 مرات لتنزيل الملصق
            for attempt in range(3):
                await client.download_media(media, file_name=sticker_path)
                await asyncio.sleep(1)  # تأخير لضمان اكتمال التنزيل
                
                if os.path.exists(sticker_path) and os.path.getsize(sticker_path) > 0:
                    break
                logger.warning(f"⚠️ محاولة {attempt + 1} فاشلة لتنزيل الملصق: {sticker_path}")
            else:
                logger.error(f"❌ فشل نهائي في تنزيل الملصق: {sticker_path}")
                return
            
            # تحويل الملصق إلى فيديو باستخدام FFmpeg
            converted_video = f"temp_{message.id}_converted.mp4"
            command = [
                "ffmpeg", "-y", "-loop", "1", "-i", sticker_path, "-c:v", "libx264",
                "-t", "1", "-vf", "format=yuv420p", converted_video
            ]
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # التحقق من نجاح التحويل
            if not os.path.exists(converted_video) or os.path.getsize(converted_video) == 0:
                logger.error(f"⚠️ فشل تحويل الملصق إلى فيديو: {process.stderr.decode()}")
                os.remove(sticker_path) if os.path.exists(sticker_path) else None
                return  # إيقاف التنفيذ لتجنب تحليل ملف غير صالح

            file_path = converted_video
            os.remove(sticker_path) if os.path.exists(sticker_path) else None

        elif message.animation:  # GIFs يتم التعامل معها كفيديو
            media = message.animation.file_id
            file_path = f"temp_{message.id}.mp4"
        else:
            return

        # تنزيل الملف (باستثناء الملصقات التي تم تحويلها بالفعل)
        if not message.sticker:
            await client.download_media(media, file_name=file_path)
            await asyncio.sleep(1)

            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                logger.error(f"⚠️ فشل تنزيل الملف أو الملف فارغ: {file_path}")
                return

        # تحليل المحتوى
        inappropriate_detected = False

        if message.photo or message.sticker:
            results = detector.detect(file_path) if os.path.exists(file_path) else []
            if results is None:
                logger.error(f"⚠️ كاشف المحتوى أرجع None للملف: {file_path}")
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

        elif message.video or message.sticker or message.animation:
            try:
                clip = VideoFileClip(file_path)
                duration = clip.duration
            except Exception as e:
                logger.error(f"⚠️ فشل فتح الفيديو {file_path}: {str(e)}")
                return

            for t in np.arange(0, duration, FRAME_INTERVAL):
                frame_path = f"temp_frame_{message.id}_{int(t)}.jpg"
                try:
                    clip.save_frame(frame_path, t=t)
                except Exception as e:
                    logger.error(f"⚠️ فشل استخراج الإطار عند {t} ثانية: {str(e)}")
                    continue

                if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
                    logger.warning(f"⚠️ الإطار عند {t} ثانية غير صالح.")
                    continue

                results = detector.detect(frame_path)
                if results is None:
                    logger.error(f"⚠️ كاشف المحتوى أرجع None للإطار: {frame_path}")
                    continue

                for obj in results:
                    if obj['class'] in [
                        'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
                        'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
                        'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
                        'FEMALE_GENITALIA_EXPOSED'
                    ] and obj['score'] >= THRESHOLD:
                        inappropriate_detected = True
                        logger.info(f"تم الكشف عن: {obj['class']} بثقة {obj['score']} في الإطار عند {t:.2f} ثانية")
                        break

                os.remove(frame_path) if os.path.exists(frame_path) else None

                if inappropriate_detected:
                    break

            clip.close()

        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذفه خلال 5 ثوانٍ.")
            await asyncio.sleep(5)
            await message.delete()
            logger.info(f"🗑️ تم حذف رسالة غير لائقة في {message.chat.id}")

        # تنظيف الملفات المؤقتة
        os.remove(file_path) if os.path.exists(file_path) else None
        os.remove(converted_video) if converted_video and os.path.exists(converted_video) else None

    except Exception as e:
        logger.error(f"⚠️ خطأ أثناء معالجة الملف: {str(e)}")
