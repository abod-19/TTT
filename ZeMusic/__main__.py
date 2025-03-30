import asyncio
import importlib

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from ZeMusic import LOGGER, app, userbot
from ZeMusic.core.call import Mody
from ZeMusic.misc import sudo
from ZeMusic.plugins import ALL_MODULES
from ZeMusic.utils.database import get_banned_users, get_gbanned, get_client
from config import BANNED_USERS

# نص الرد التلقائي
AUTO_REPLY_TEXT = "مرحبًا! أنا روبوت مساعد، كيف يمكنني مساعدتك؟"

async def start_auto_reply():
    """
    تهيئة الحساب المساعد للرد التلقائي على أي رسالة خاصة يتم استقبالها.
    """
    from ZeMusic.core.userbot import assistants
    if not assistants:
        LOGGER("AutoReply").error("لا يوجد حسابات مساعدة متاحة.")
        return

    num = assistants[0]  # استخدام أول حساب مساعد فقط
    client = await get_client(num)

    @client.on_message(filters.private & ~filters.me)
    async def reply_auto(client, message):
        try:
            await message.reply_text(AUTO_REPLY_TEXT)
        except Exception as e:
            LOGGER("AutoReply").error(f"خطأ أثناء الرد التلقائي: {e}")

    LOGGER("AutoReply").info("تم تشغيل نظام الرد التلقائي للحساب المساعد.")
    await client.start()
    await client.idle()  # إبقاء العميل المساعد قيد التشغيل

async def init():
    """
    الدالة الرئيسية للمشروع: تهيئة البوت والحسابات المساعدة، واستيراد الوحدات، وتشغيل الاتصال بالصوت،
    وتشغيل الرد التلقائي في مهمة منفصلة.
    """
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("ZeMusic.plugins" + all_module)
    LOGGER("ZeMusic.plugins").info("تنزيل معلومات السورس...")
    await userbot.start()
    await Mody.start()

    try:
        await Mody.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("ZeMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except Exception:
        pass

    await Mody.decorators()
    LOGGER("ZeMusic").info(
        "جاري تشغيل البوت\nتم التنصيب على سورس الملك بنجاح\nقناة السورس https://t.me/EF_19"
    )
    
    # تشغيل الرد التلقائي في مهمة منفصلة للحساب المساعد
    asyncio.create_task(start_auto_reply())
    
    await idle()
    await app.stop()
    await userbot.stop()
    # تأكد من تعريف دالة azkar() أو قم بإزالتها إن لم تكن مستخدمة.
    try:
        await azkar()
    except Exception:
        pass
    LOGGER("ZeMusic").info("Stopping Ze Music Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
    
