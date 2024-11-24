import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
from ZeMusic import app
from ZeMusic.plugins.play.filters import command

lnk = "https://t.me/" + config.CHANNEL_LINK
Nem = f"{config.BOT_NAME} ابحث"
Nam = f"{config.BOT_NAME} بحث"

def remove_if_exists(path):
    """حذف الملفات المؤقتة إذا كانت موجودة"""
    if os.path.exists(path):
        os.remove(path)

@app.on_message(command(["song", "/song", "بحث", Nem, Nam]))
async def song_downloader(client, message: Message):
    if message.text in ["song", "/song", "بحث", Nem, Nam]:
        return
    elif message.command[0] in config.BOT_NAME:
        query = " ".join(message.command[2:])
    else:
        query = " ".join(message.command[1:])
        
    m = await message.reply_text("<b>جـارِ البحث ♪</b>")

    try:
        # البحث عن الأغنية في SoundCloud
        search_url = f"https://soundcloud.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        
        if response.status_code != 200:
            await m.edit(f"- خطأ في الاتصال بـ SoundCloud (الكود: {response.status_code}).")
            print(f"HTTP Error: {response.status_code} - {response.text}")
            return

        # استخراج الروابط باستخدام BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        tracks = soup.find_all("a", class_="soundTitle__title")
        
        if not tracks:
            await m.edit("- لم يتم العثور على أي نتائج. حاول مرة أخرى.")
            print("No tracks found in the search results.")
            return

        # أخذ أول نتيجة
        track_url = f"https://soundcloud.com{tracks[0]['href']}"

        await m.edit("<b>جاري التحميل من SoundCloud...</b>")
        
        # تنزيل الأغنية باستخدام scdl
        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)
        process = subprocess.run(
            ["scdl", "-l", track_url, "-o", output_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if process.returncode != 0:
            await m.edit("- فشل في تنزيل الملف. تحقق من SoundCloud أو المكتبة المستخدمة.")
            print(f"scdl Error:\n{process.stderr.decode()}")
            return

        # العثور على الملف الذي تم تنزيله
        downloaded_files = os.listdir(output_dir)
        if not downloaded_files:
            await m.edit("- لم يتم العثور على أي ملفات تم تنزيلها.")
            print("No downloaded files found in the output directory.")
            return

        audio_file = os.path.join(output_dir, downloaded_files[0])

        # إرسال الملف الصوتي
        await message.reply_audio(
            audio=audio_file,
            caption=f"<pre>⟡ {app.mention}</pre>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=config.CHANNEL_NAME, url=lnk),
                    ],
                ]
            ),
        )
        await m.delete()

    except Exception as e:
        await m.edit(f"حدث خطأ أثناء العملية: {str(e)}")
        print(f"Unexpected Error: {str(e)}")

    # حذف الملفات المؤقتة
    try:
        remove_if_exists(audio_file)
    except Exception as e:
        print(f"Error while removing temporary files: {str(e)}")
