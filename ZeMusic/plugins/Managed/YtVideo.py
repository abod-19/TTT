import future

import asyncio
import os
import time
from urllib.parse import urlparse

import wget
from pyrogram import filters
from pyrogram.types import Message
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL
from ZeMusic.platforms.Youtube import cookie_txt_file
from ZeMusic import app


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def get_text(message: Message) -> [None, str]:
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@app.on_message(filters.command(["فيد", "yt", "تحميل", "تحميل فيديو"],""))
async def ytmusic(client, message: Message):
    urlissed = get_text(message)
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chutiya = f"<a href='tg://user?id={user_id}'>{user_name}</a>"

    pablo = await message.reply_text("<b>جاري البحث عن المقطع..</b>")
    if not urlissed:
        await pablo.edit(
            "- لم يتم العثـور على نتائج حاول مجددا"
        )
        return

    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    thums = mio[0]["channel"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
        "cookiefile": cookie_txt_file(),
    }
    try:
        with YoutubeDL(opts) as ytdl:
            infoo = ytdl.extract_info(url, False)
            round(infoo["duration"] / 60)
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(f"فشل في التحميل \nالخطاء : {str(e)}")
        return
    c_time = time.time()
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"❄ <b>ᴛɪᴛʟᴇ :</b> <a href='{mo}'>{thum}</a>\n🥀 <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {chutiya}"
    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        progress_args=(
            pablo,
            c_time,
            f"جاري تحميل `{urlissed}` من يوتيوب..",
            file_stark,
        ),
        reply_to_message_id=message.id,
    )
    await pablo.delete()
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)


__mod_name__ = "فيد"
__help__ = """ 'فيد' لتحميل فيديو من اليوتيب """
