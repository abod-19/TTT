import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ZeMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from ZeMusic.core.call import Mody
from ZeMusic.utils import seconds_to_min, time_to_seconds
from ZeMusic.utils.channelplay import get_channeplayCB
from ZeMusic.utils.decorators.language import languageCB
from ZeMusic.utils.decorators.play import PlayWrapper
from ZeMusic.utils.formatters import formats
from ZeMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from ZeMusic.utils.logger import play_logs
from ZeMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical

Nem = config.BOT_NAME + " شغل"
@app.on_message(
    filters.command(
        [
            "play",
            "تشغيل",
            "شغل",
            "فيديو",
            Nem,
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ],""
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
    else:
        return await mystic.edit_text("يرجى توفير رابط من SoundCloud.")

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    # يتم الإبقاء فقط على معالجة SoundCloud هنا أيضًا.
    pass
