from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pyrogram.errors import ChannelPrivate

from config import PLAYLIST_IMG_URL, SUPPORT_CHAT
from config import adminlist
from strings import get_string
from ZeMusic import YouTube, app
from ZeMusic.core.call import Mody
from ZeMusic.misc import SUDOERS
from ZeMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from ZeMusic.utils.inline import botplaylist_markup

links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
        
        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )
        url = await YouTube.url(message)
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await message.reply_photo(
                    photo=PLAYLIST_IMG_URL,
                    caption=_["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None
        try:
            is_call_active = (await app.get_chat(chat_id)).is_call_active
            if not is_call_active:
                return await message.reply_text(
                    "- لم يتم العثور على مكالمه نشطة.\n- يرجى تشغيل المكالمه والمحاولة مجدداً."
                )
        except Exception:
            pass

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                else:
                    if message.from_user.id not in admins:
                        return await message.reply_text(_["play_4"])
        
        if message.command[0][0] == "v" or message.command[0][0] == "ف":
            video = True
        else:
            if "-v" in message.text:
                video = True
            else:
                video = True if message.command[0][1] == "v" else None
        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None
            
        if await is_active_chat(chat_id):
            userbot = await get_assistant(message.chat.id)
            try:
                call_participants_id = [
                    member.chat.id
                    async for member in userbot.get_call_members(chat_id)
                    if member.chat
                ]
                # Checking if assistant id not in list so clear queues and remove active voice chat and process

                if not call_participants_id or userbot.id not in call_participants_id:
                    await Mody.stop_stream(chat_id)
            except ChannelPrivate:
                pass 

        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
