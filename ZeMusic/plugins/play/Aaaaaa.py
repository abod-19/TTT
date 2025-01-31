from ZeMusic import app
from pyrogram import filters
import os
import logging
import asyncio
import aiofiles
import numpy as np
from nudenet import NudeDetector
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

detector = NudeDetector()
ALLOWED_GROUPS = []
THRESHOLD = 0.35
FRAME_INTERVAL = 1.0

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def convert_webp_to_png(webp_path, png_path):
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
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # حذف الملصقات من النوعين webp و webm فورًا
        if message.sticker:
            mime_type = message.sticker.mime_type
            if mime_type in ["image/webp", "video/webm"]:
                await message.delete()
                logger.info(f"تم حذف ملصق من نوع {mime_type}")
                return

        if message.photo:
            media = message.photo.file_id
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            media = message.video.file_id
            file_path = f"temp_{message.id}.mp4"
        elif message.animation:
            media = message.animation.file_id
            file_path = f"temp_{message.id}.mp4"
        else:
            return

        media_bytes_io = await client.download_media(media, in_memory=True)
        if not media_bytes_io:
            logger.error("فشل تنزيل الملف: media_bytes_io هو None")
            return

        media_data = media_bytes_io.getvalue()
        if not media_data:
            logger.error("الملف الذي تم تنزيله فارغ!")
            return

        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(media_data)

        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.error(f"فشل في حفظ الملف: {file_path} غير موجود أو فارغ")
            return

        inappropriate_detected = False

        if message.photo or message.animation:
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

        elif message.video:
            try:
                with VideoFileClip(file_path) as clip:
                    duration = clip.duration

                    for t in np.arange(0, duration, FRAME_INTERVAL):
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

                        if os.path.exists(frame_path):
                            os.remove(frame_path)

                        if inappropriate_detected:
                            break

            except Exception as e:
                logger.error(f"فشل فتح الفيديو {file_path}: {str(e)}")
                return

        if inappropriate_detected:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذف الملف خلال 5 ثوانٍ.")
            await asyncio.sleep(5)
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")

    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {str(e)}")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
