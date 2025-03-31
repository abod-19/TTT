from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
import config
from ..logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        # تهيئة الحساب المساعد
        self.one = Client(
            name="ZeAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            # no_updates=False (تم إزالته لأنه افتراضيًا False)
        )
        # إضافة Handler للرد التلقائي
        self.one.add_handler(MessageHandler(self.auto_reply, filters.private & ~filters.me))

    async def auto_reply(self, client, message):
        """دالة الرد التلقائي على الرسائل الخاصة."""
        try:
            await message.reply_text("مرحبًا! أنا مساعد تلقائي، كيف يمكنني مساعدتك؟")
        except Exception as e:
            LOGGER(__name__).error(f"خطأ في الرد التلقائي: {e}")

    async def start(self):
        """بدء تشغيل الحساب المساعد."""
        LOGGER(__name__).info("جاري تشغيل الحساب المساعد...")
        
        if config.STRING1:
            try:
                await self.one.start()
                # إجراءات ما بعد التشغيل
                await self.post_start()
            except Exception as e:
                LOGGER(__name__).error(f"فشل في تشغيل الحساب المساعد: {e}")
                exit()

    async def post_start(self):
        """إجراءات ما بعد بدء التشغيل."""
        try:
            # الانضمام إلى القنوات
            await self.one.join_chat("EF_19")
            await self.one.join_chat("jnssghb")
        except Exception as e:
            LOGGER(__name__).warning(f"فشل الانضمام إلى القناة: {e}")

        # إرسال رسالة إلى مجموعة السجل
        try:
            await self.one.send_message(config.LOGGER_ID, "『 تم تشغيل البوت على سورس الملك 』")
        except Exception as e:
            LOGGER(__name__).error(f"فشل إرسال الرسالة إلى مجموعة السجل: {e}")
            exit()

        # حفظ معلومات الحساب المساعد
        self.one.id = (await self.one.get_me()).id
        self.one.name = (await self.one.get_me()).first_name
        self.one.username = (await self.one.get_me()).username
        assistantids.append(self.one.id)
        assistants.append(1)
        LOGGER(__name__).info(f"المساعد {self.one.name} يعمل الآن!")

    async def stop(self):
        """إيقاف الحساب المساعد."""
        LOGGER(__name__).info("إيقاف الحساب المساعد...")
        try:
            await self.one.stop()
        except Exception as e:
            LOGGER(__name__).error(f"فشل في إيقاف الحساب المساعد: {e}")
