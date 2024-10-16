import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from ZeMusic import app
from ZeMusic.utils.database import get_served_chats
from config import OWNER_ID, LOGGER_ID
from pyrogram.enums import ChatMemberStatus
from datetime import datetime, timedelta

photo_urls = [
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
]

@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    chat = message.chat
    dev_id = OWNER_ID
    new_members = message.new_chat_members
    bot_id = (await client.get_me()).id

    for new_member in new_members:
        if new_member.id == dev_id:
            await welcome_owner(client, message, new_member)
        elif new_member.id == bot_id:
            await handle_bot_addition(client, message)
        else:
            await welcome_new_members(client, message, new_member)

async def welcome_owner(client: Client, message: Message, new_member):
    chat_id = message.chat.id
    dev_id = OWNER_ID
    info = await app.get_chat(dev_id)
    name = info.first_name
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(name, user_id=dev_id)]])
    
    photos = [photo async for photo in client.get_chat_photos(dev_id, limit=1)]
    
    if not photos:
        await message.reply_text(
            f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",
            reply_markup=markup
        )
    else:
        await message.reply_photo(
            photos[0].file_id,
            caption=f"↢ مرحباً مطوري <a href='tg://user?id={dev_id}'>{name}</a> نورت الشات ياعزيزي🧸",
            reply_markup=markup
        )

async def handle_bot_addition(client: Client, message: Message):
    chat = message.chat
    added_by = message.from_user.first_name if message.from_user else "مستخدم غير معروف"
    added_id = message.from_user.id
    served_chats = len(await get_served_chats())
    cont = await app.get_chat_members_count(chat.id)
    chatusername = message.chat.username or "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜ𝑝"
    
    caption = (
        f"🌹 تمت إضافة البوت إلى مجموعة جديدة.\n\n"
        f" <b>𝙲𝙷𝙰𝚃</b> › : {chat.title}\n"
        f" <b>𝙲𝙷𝙰𝚃 𝙸𝙳</b> › : {chat.id}\n"
        f" <b>𝙲𝙷𝙰𝚃 𝚄𝙽𝙰𝙼𝙴</b> › : @{chatusername}\n"
        f" <b>𝙲𝙾𝚄𝙽𝚃</b> › : {cont}\n"
        f" <b>𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂</b> › : {served_chats}\n"
        f" <b>𝙰𝙳𝙳𝙴𝙳 𝙱𝚈</b> › : <a href='tg://user?id={added_id}'>{added_by}</a>"
    )
    
    await app.send_photo(
        LOGGER_ID,
        photo=random.choice(photo_urls),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(added_by, url=f"tg://openmessage?user_id={added_id}")]]
        )
    )

async def welcome_new_members(client: Client, message: Message, new_member):
    chat = await app.get_chat(message.chat.id)
    chat_photo = chat.photo
    owner = await get_chat_owner(client, chat.id)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(owner['name'], url=f"tg://openmessage?user_id={owner['id']}")]]
    )

    now = datetime.utcnow() + timedelta(hours=3)
    welcome_text = (
        f"𝐰𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩.🧸\n\n"
        f"__{chat.title}__\n\n"
        f"➥• Welcome  : {new_member.mention}\n"
        f"➥• User : @{new_member.username or 'No username'}\n"
        f"➥• time : {now.strftime('%I:%M %p')}\n"
        f"➥• date : {now.strftime('%Y/%m/%d')}"
    )

    if chat_photo:
        photo_file = await client.download_media(chat_photo.big_file_id)
        await message.reply_photo(photo=photo_file, caption=welcome_text, reply_markup=keyboard)
    else:
        await message.reply_text(welcome_text, reply_markup=keyboard)

async def get_chat_owner(client: Client, chat_id: int):
    async for member in client.get_chat_members(chat_id):
        if member.status == ChatMemberStatus.OWNER:
            return {'id': member.user.id, 'name': member.user.first_name}
