from pyrogram import Client, filters
import config

class Rd:
    def __init__(self):
        self.one = Client(
            name="abod",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

    async def start(self):
        # بدء الجلسة
        await self.one.start()
        print("الجلسة قيد التشغيل...")

        # إضافة الرد التلقائي
        @self.one.on_message(filters.private & ~filters.me)
        async def auto_reply(client, message):
            reply_text = "عندك اي مشكله قم بمراسله المطور @BBFYY"
            await message.reply_text(reply_text)

        print("الرد التلقائي مفعل.")
        await self.one.idle()

    async def stop(self):
        await self.one.stop()
        print("تم إيقاف الجلسة.")
