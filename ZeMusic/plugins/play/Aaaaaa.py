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

async def analyze_media(file_path, is_video=False):
    inappropriate_detected = False
    
    if is_video:
        try:
            with VideoFileClip(file_path) as clip:
                duration = clip.duration
                for t in np.arange(0, duration, FRAME_INTERVAL):
                    frame_path = f"temp_frame_{os.path.basename(file_path)}_{int(t)}.jpg"
                    try:
                        clip.save_frame(frame_path, t=t)
                    except Exception as e:
                        logger.error(f"فشل استخراج الإطار: {str(e)}")
                        continue

                    if os.path.exists(frame_path) and os.path.getsize(frame_path) > 0:
                        results = detector.detect(frame_path)
                        inappropriate_detected = check_results(results)
                        os.remove(frame_path)
                        
                    if inappropriate_detected:
                        break
        except Exception as e:
            logger.error(f"فشل تحليل الفيديو: {str(e)}")
    else:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            results = detector.detect(file_path)
            inappropriate_detected = check_results(results)
            
    return inappropriate_detected

def check_results(results):
    for obj in results:
        if obj['class'] in [
            'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
            'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
            'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
            'FEMALE_GENITALIA_EXPOSED'
        ] and obj['score'] >= THRESHOLD:
            logger.info(f"تم الكشف عن: {obj['class']} بثقة {obj['score']}")
            return True
    return False

@app.on_message(filters.group & (filters.photo | filters.video | filters.sticker | filters.animation))
async def check_media(client, message):
    try:
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        file_path = None
        is_video = False
        
        # تحديد نوع الملف
        if message.sticker:
            mime_type = message.sticker.mime_type
            if mime_type == "image/webp":
                file_path = f"temp_{message.id}.webp"
                converted_path = f"temp_{message.id}.png"
            elif mime_type == "video/webm":
                file_path = f"temp_{message.id}.webm"
                is_video = True
            else:
                return
        elif message.photo:
            file_path = f"temp_{message.id}.jpg"
        elif message.video:
            file_path = f"temp_{message.id}.mp4"
            is_video = True
        elif message.animation:
            file_path = f"temp_{message.id}.mp4"
            is_video = True

        if not file_path:
            return

        # تنزيل الملف
        media = await client.download_media(message, file_name=file_path)
        if not media or not os.path.exists(file_path):
            logger.error("فشل تنزيل الملف")
            return

        # معالجة خاصة للملصقات
        if message.sticker:
            if mime_type == "image/webp":
                if await convert_webp_to_png(file_path, converted_path):
                    inappropriate = await analyze_media(converted_path)
                    os.remove(converted_path)
                else:
                    inappropriate = False
            elif mime_type == "video/webm":
                inappropriate = await analyze_media(file_path, is_video=True)
        else:
            inappropriate = await analyze_media(file_path, is_video=is_video)

        # الحذف إذا تم اكتشاف محتوى غير لائق
        if inappropriate:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم حذف الملف خلال 5 ثوانٍ.")
            await asyncio.sleep(5)
            await message.delete()
            logger.info(f"تم حذف رسالة غير لائقة في {message.chat.id}")

    except Exception as e:
        logger.error(f"خطأ في المعالجة: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
