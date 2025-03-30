import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from ZeMusic import app
from ZeMusic.misc import SUDOERS
from ZeMusic.utils.database import get_client
from ZeMusic.utils.decorators.language import language
from config import OWNER_ID
from pyrogram.enums import ChatType

IS_BROADCASTING = False

@app.on_message(filters.command(["اذ"], "") & SUDOERS)
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["broad_2"])
    
    query = message.text.split(None, 1)[1] if not message.reply_to_message else None
    if query and query.strip() == "":
        return await message.reply_text(_["broad_8"])
    
    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])
    
    aw = await message.reply_text(_["broad_5"])
    text = _["broad_6"]
    from ZeMusic.core.userbot import assistants
    
    if not assistants:
        return await message.reply_text("لا يوجد حسابات مساعدة متاحة.")
    
    # استخدام أول حساب فقط من القائمة
    num = assistants[0]
    sent = 0
    client = await get_client(num)
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type == ChatType.PRIVATE:
            try:
                if message.reply_to_message:
                    await client.forward_messages(dialog.chat.id, message.chat.id, message.reply_to_message.id)
                else:
                    await client.send_message(dialog.chat.id, text=query)
                sent += 1
                await asyncio.sleep(3)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except:
                continue
    
    text += _["broad_7"].format(num, sent)
    
    try:
        await aw.edit_text(text)
    except:
        pass
    
    IS_BROADCASTING = False
