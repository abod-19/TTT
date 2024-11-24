from pyrogram import filters
from pyrogram.types import Message
from config import BANNED_USERS
import config
from ZeMusic.platforms.Soundcloud import SoundAPI  # تأكد من مسار الاستيراد حسب مكان الكود
from ZeMusic.utils.decorators.play import PlayWrapper
from ZeMusic.utils.stream.stream import stream

@app.on_message(
    filters.command(
        [
            "play",
            "تشغيل",
            "شغل",
            "فيديو",
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ], ""
    )
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text("جاري تشغيل المقطع...")
    user_id = message.from_user.id if message.from_user else "1121532100"
    user_name = message.from_user.first_name if message.from_user else "None"

    # إذا كان هناك نص مرفق بالرسالة (مثل "ماجد المهندس احبك")
    if not url:
        text = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
        if text:
            try:
                # البحث عن الأغنية في SoundCloud باستخدام النص المدخل
                sound_api = SoundAPI()  # تأكد من أنك أنشأت الكائن بشكل صحيح
                track_details = await sound_api.search(text)
                
                if not track_details:
                    return await mystic.edit_text("لم يتم العثور على أي أغنية بهذه الكلمات.")
                
                track_url = track_details['url']
                track_duration = track_details['duration_sec']
                
                # التحقق من المدة
                if track_duration > config.DURATION_LIMIT:
                    return await mystic.edit_text(
                        f"المدة تتجاوز الحد المسموح به وهو {config.DURATION_LIMIT_MIN} دقيقة."
                    )

                # بدء بث الأغنية
                await stream(
                    _,
                    mystic,
                    user_id,
                    track_details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",  # نستخدم "soundcloud" هنا
                    forceplay=fplay,
                )
            except Exception as e:
                return await mystic.edit_text(f"حدث خطأ أثناء البحث أو التشغيل: {str(e)}")
            return await mystic.delete()
        else:
            return await mystic.edit_text("يرجى توفير نص للأغنية.")
    
    # إذا كان هناك رابط، يتم معالجته كما هو موجود في الكود الحالي.
    if url:
        if await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except:
                return await mystic.edit_text("فشل في جلب المقطع من SoundCloud.")
            
            duration_sec = details["duration_sec"]
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    f"المدة تتجاوز الحد المسموح به وهو {config.DURATION_LIMIT_MIN} دقيقة."
                )

            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",
                    forceplay=fplay,
                )
            except Exception as e:
                return await mystic.edit_text(f"حدث خطأ أثناء التشغيل: {str(e)}")
            return await mystic.delete()
        else:
            return await mystic.edit_text("رابط غير صالح لـ SoundCloud.")
