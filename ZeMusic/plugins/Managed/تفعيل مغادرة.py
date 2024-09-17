"""
import os
import aiohttp
import aiofiles
from pyrogram import Client, filters
from pyrogram.types import Message
from ZeMusic import app
from ZeMusic.plugins.play.filters import command
import config
from config import OWNER_ID
from ZeMusic.utils.database import is_log_enabled, enable_log, disable_log



@app.on_message(command(["تفعيل المغادرة", "تفعيل المغادره"]) & filters.user(OWNER_ID))
async def enable_log_comm(client, message: Message):
    if await is_log_enabled():
        await message.reply_text("<b>المغادرة مفعل من قبل.</b>")
        return
    await enable_log()
    await message.reply_text("<b>تم تفعيل المغادرة بنجاح.</b>")
  

@app.on_message(command(["تعطيل المغادره", "تعطيل المغادرة"]) & filters.user(OWNER_ID))
async def disable_log_comm(client, message: Message):
    if not await is_log_enabled():
        await message.reply_text("<b>المغادرة معطل من قبل.</b>")
        return
    await disable_log()
    await message.reply_text("<b>تم تعطيل المغادرة بنجاح.</b>")
"""
