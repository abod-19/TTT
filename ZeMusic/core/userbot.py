from pyrogram import Client, filters
import config
from ..logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="ZeAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

    async def start(self):
        LOGGER(__name__).info(f"جلب معلومات السورس...")
        if config.STRING1:
            await self.one.start()
            try:
                await self.one.join_chat("EF_19")
                await self.one.join_chat("jnssghb")
            except Exception as e:
                LOGGER(__name__).error(f"Error joining chat: {e}")
                pass
            assistants.append(1)
            try:
                await self.one.send_message(config.LOGGER_ID, "『 تم تشغيل البوت على سورس الملك 』")
            except Exception as e:
                LOGGER(__name__).error(
                    f"Assistant Account 1 has failed to access the log Group: {e}. Make sure your assistant is added to the log group!"
                )
                exit()
            self.one.id = (await self.one.get_me()).id
            self.one.name = (await self.one.get_me()).mention
            self.one.username = (await self.one.get_me()).username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"تم تشغيل المساعد {self.one.name} على سورس الملك")

            # إضافة ميزة الرد التلقائي
            @self.one.on_message(filters.private & ~filters.me)
            async def auto_reply(client, message):
                try:
                    await message.reply_text("مرحبًا! أنا مساعد تلقائي، كيف يمكنني مساعدتك؟")
                except Exception as e:
                    LOGGER(__name__).error(f"Error replying to message: {e}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Assistant One...")
        try:
            if config.STRING1:
                await self.one.stop()
        except Exception as e:
            LOGGER(__name__).error(f"Error stopping assistant: {e}")
            pass
