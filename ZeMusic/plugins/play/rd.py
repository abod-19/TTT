from pyrogram import Client, filters
import config

@Client.on_message()
async def auto_reply(client, message):
    print(f"رسالة جديدة من {message.from_user.id}: {message.text}")
    reply_text = "عندك اي مشكله قم بمراسله المطور @BBFYY"
    await message.reply_text(reply_text)
    
    print("الرد التلقائي مفعل.")
