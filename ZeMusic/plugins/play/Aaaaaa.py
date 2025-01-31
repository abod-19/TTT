from ZeMusic import app
from pyrogram import filters, Client
import os
import logging
import asyncio
import aiofiles
import numpy as np
from nudenet import NudeDetector
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
from tempfile import gettempdir

detector = NudeDetector()
ALLOWED_GROUPS = []
THRESHOLD = 0.35
FRAME_INTERVAL = 1.0

# إعداد مجلد مؤقت خاص للتطبيق
TEMP_DIR = os.path.join(gettempdir(), "ZeMusic")
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def safe_download(client: Client, message, file_path: str) -> bool:
    """تنزيل الملف مع معالجة الأخطاء المحسنة"""
    try:
        download_path = await client.download_media(
            message,
            file_name=file_path,
            in_memory=False
        )
        return os.path.exists(download_path) and os.path.getsize(download_path) > 0
    except Exception as e:
        logger.error(f"فشل التنزيل: {str(e)}")
        return False

async def convert_webp_to_png(webp_path: str) -> str:
    """تحويل WEBP إلى PNG مع تعقب الأخطاء"""
    png_path = os.path.join(TEMP_DIR, f"{os.path.basename(webp_path)}.png")
    try:
        with Image.open(webp_path) as img:
            img.save(png_path, "PNG")
        return png_path
    except Exception as e:
        logger.error(f"فشل التحويل: {str(e)}")
        return None

async def analyze_media(file_path: str, is_video: bool = False) -> bool:
    """تحليل المحتوى مع تعزيز معالجة الأخطاء"""
    try:
        if is_video:
            with VideoFileClip(file_path) as clip:
                duration = clip.duration
                for t in np.arange(0, duration, FRAME_INTERVAL):
                    frame_path = os.path.join(TEMP_DIR, f"frame_{os.path.basename(file_path)}_{int(t)}.jpg")
                    try:
                        clip.save_frame(frame_path, t=t)
                        if check_results(detector.detect(frame_path)):
                            return True
                    finally:
                        if os.path.exists(frame_path):
                            os.remove(frame_path)
        else:
            return check_results(detector.detect(file_path))
    except Exception as e:
        logger.error(f"فشل التحليل: {str(e)}")
    return False

def check_results(results: list) -> bool:
    """فحص النتائج بكفاءة"""
    target_classes = {
        'EXPOSED_ANUS', 'COVERED_GENITALIA', 'EXPOSED_GENITALIA',
        'FEMALE_GENITALIA_COVERED', 'BUTTOCKS_EXPOSED',
        'FEMALE_BREAST_EXPOSED', 'MALE_GENITALIA_EXPOSED',
        'FEMALE_GENITALIA_EXPOSED'
    }
    return any(obj['score'] >= THRESHOLD for obj in results if obj['class'] in target_classes)

@app.on_message(filters.group & (filters.photo | filters.video | filters.sticker | filters.animation))
async def enhanced_check(client: Client, message):
    """الإصدار المحسن مع معالجة أخطاء موسعة"""
    try:
        if ALLOWED_GROUPS and message.chat.id not in ALLOWED_GROUPS:
            return

        # توليد اسم ملف فريد
        file_id = message.id
        temp_file = os.path.join(TEMP_DIR, f"temp_{file_id}")

        # تحديد نوع الملف
        if message.sticker:
            mime_type = message.sticker.mime_type
            if mime_type == "image/webp":
                temp_file += ".webp"
            elif mime_type == "video/webm":
                temp_file += ".webm"
            else:
                return
        elif message.photo:
            temp_file += ".jpg"
        elif message.video or message.animation:
            temp_file += ".mp4"

        # تنزيل الملف مع التعامل مع الأخطاء
        if not await safe_download(client, message, temp_file):
            logger.error(f"فشل تنزيل الملف: {temp_file}")
            return

        # معالجة خاصة للملصقات
        if message.sticker:
            if message.sticker.mime_type == "image/webp":
                converted_path = await convert_webp_to_png(temp_file)
                if not converted_path:
                    return
                try:
                    inappropriate = await analyze_media(converted_path)
                finally:
                    os.remove(converted_path)
            else:
                inappropriate = await analyze_media(temp_file, is_video=True)
        else:
            inappropriate = await analyze_media(temp_file, is_video=message.video or message.animation)

        # إجراءات الحذف
        if inappropriate:
            await message.reply_text("⚠️ تم اكتشاف محتوى غير لائق. سيتم الحذف خلال 5 ثوانٍ.")
            await asyncio.sleep(5)
            await message.delete()
            logger.info(f"تم حذف محتوى في الدردشة {message.chat.id}")

    except Exception as e:
        logger.error(f"خطأ جسيم: {str(e)}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
