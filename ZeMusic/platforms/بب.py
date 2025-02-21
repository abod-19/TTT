async def download(
    self,
    link: str,
    mystic,
    video: Union[bool, str] = None,
    videoid: Union[bool, str] = None,
    songaudio: Union[bool, str] = None,
    songvideo: Union[bool, str] = None,
    format_id: Union[bool, str] = None,
    title: Union[bool, str] = None,
) -> str:
    if videoid:
        link = self.base + link

    # التحقق من وجود الملف في قاعدة البيانات
    existing_entry = await songdb.find_one({"video_id": videoid})
    if existing_entry:
        return existing_entry["channel_link"], False  # False يعني أن الملف موجود في القناة

    # إذا لم يكن موجودًا، تابع التنزيل
    loop = asyncio.get_running_loop()

    async def audio_dl():
        ydl_optssx = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": f"{await cookies()}",
        }

        x = YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    async def video_dl():
        ydl_optssx = {
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": f"{await cookies()}",
        }

        x = YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    if songvideo:
        return await song_video_dl()
    elif songaudio:
        return await song_audio_dl()
    elif video:
        if await is_on_off(1):
            direct = True
            downloaded_file = await video_dl()
        else:
            command = [
                "yt-dlp",
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                f"--cookies {await cookies()}",
                link,
            ]

            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if stdout:
                downloaded_file = stdout.decode().split("\n")[0]
                direct = None
            else:
                downloaded_file = await video_dl()
                direct = True
    else:
        direct = True
        downloaded_file = await audio_dl()

    # بعد التنزيل، إرسال الملف إلى القناة وحفظ الرابط في قاعدة البيانات
    message_to_channel = await app.send_audio(
        chat_id="@IC_I6",  # تأكد من تغيير هذا إلى معرف قناتك
        audio=downloaded_file,
        caption=f"{videoid}",
    )
    await songdb.insert_one({
        "video_id": videoid,
        "channel_link": message_to_channel.link,
    })

    return downloaded_file, direct
