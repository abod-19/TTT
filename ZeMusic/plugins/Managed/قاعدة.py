import requests
import random
import os
import re
import asyncio
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant
import asyncio
import random
from ZeMusic.utils.database import add_served_chat
from ZeMusic import app

@app.on_message(filters.command(["ا", "هلا", "سلام", "المالك", "بخير", "وانت"],"") & filters.group)
async def bot_check(_, client: Client, message: Message):
    chat_id = message.chat.id
    await add_served_chat(chat_id)
