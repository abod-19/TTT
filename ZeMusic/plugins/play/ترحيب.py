import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from ZeMusic import app
from ZeMusic.utils.database import get_served_chats
from config import OWNER_ID, LOGGER_ID
from pyrogram.enums import ChatMemberStatus
from datetime import datetime, timedelta
from ZeMusic.plugins.play.filters import command
from ZeMusic.utils.decorators import AdminActual
from ZeMusic.utils.database import is_welcome_enabled, enable_welcome, disable_welcome
import requests
photo_urls = [
    "https://envs.sh/Wi_.jpg",
    "https://envs.sh/Wi_.jpg",
]

@app.on_message(filters.new_chat_members, group=-2)
async def welcome_new_member(client: Client, message: Message):
    chat = message.chat
    dev_id = OWNER_ID
    bot_id = (await client.get_me()).id

    for new_member in message.new_chat_members:
        # ترحيب بمطور البوت
        if new_member.id == dev_id:
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
        
        # التعامل مع إضافة البوت إلى مجموعة جديدة
        if new_member.id == bot_id:
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
        
        # ترحيب بالأعضاء الجدد
        else:
            chat_id = message.chat.id  # الحصول على معرف الدردشة
            if not await is_welcome_enabled(chat_id):
                return
            chat_photo = chat.photo
            async for member in client.get_chat_members(chat.id):
                if member.status == ChatMemberStatus.OWNER:
                    owner_id = member.user.id
                    owner_name = member.user.first_name
                    break
            
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(owner_name, url=f"tg://openmessage?user_id={owner_id}")]]
            )

            now = datetime.utcnow() + timedelta(hours=3)

            if chat_photo:
                photo_file = await client.download_media(chat_photo.big_file_id)
                with open(photo_file, "rb") as f:
                    data = f.read()
                    resp = requests.post("https://envs.sh", files={"file": data})
        
                if resp.status_code == 200:
                    upload_url = f"{resp.text}"    
            
                try:
                    os.remove(photo_file)
                except Exception as error:
                    print(error)
                welcome_text = (
                    f"<a href='{upload_url}'>رابط الصوره</a>\n"
                    f"𝐰𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩.🧸\n\n"
                    f"{chat.title}\n\n"
                    f"➥• Welcome  : {new_member.mention}\n"
                    f"➥• User : @{new_member.username or 'No username'}\n"
                    f"➥• time : {now.strftime('%I:%M %p')}\n"
                    f"➥• date : {now.strftime('%Y/%m/%d')}"
                )
                # إرسال النص مع تفعيل وضع الويب تلقائياً (preview)
                await message.reply_text(welcome_text, reply_markup=keyboard, disable_web_page_preview=False)
            else:
                welcome_text = (
                    f"𝐰𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩.🧸\n\n"
                    f"{chat.title}\n\n"
                    f"➥• Welcome  : {new_member.mention}\n"
                    f"➥• User : @{new_member.username or 'No username'}\n"
                    f"➥• time : {now.strftime('%I:%M %p')}\n"
                    f"➥• date : {now.strftime('%Y/%m/%d')}"
                )
                await message.reply_text(welcome_text, reply_markup=keyboard)

# أمر للتعطيل
@app.on_message(command(["تعطيل الترحيب الذكي"]) & filters.group)
@AdminActual
async def disable_welcome_command(client, message: Message, _):
    chat_id = message.chat.id  # الحصول على معرف الدردشة
    if not await is_welcome_enabled(chat_id):
        await message.reply_text("<b>الترحيب الذكي معطل من قبل.</b>")
        return
    await disable_welcome(chat_id)
    await message.reply_text("<b>تم تعطيل الترحيب الذكي بنجاح.</b>")

#######&&&&&&#######

#امر للتفعيل
@app.on_message(command(["تفعيل الترحيب الذكي"]) & filters.group)
@AdminActual
async def enable_welcome_command(client, message: Message, _):
    chat_id = message.chat.id  # الحصول على معرف الدردشة
    if await is_welcome_enabled(chat_id):
        await message.reply_text("<b>الترحيب الذكي مفعل من قبل.</b>")
        return
    await enable_welcome(chat_id)
    await message.reply_text("<b>تم تفعيل الترحيب الذكي بنجاح.</b>")
    
