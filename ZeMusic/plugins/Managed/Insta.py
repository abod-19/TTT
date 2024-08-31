import os
import future
import asyncio
import requests
import time
import yt_dlp
from urllib.parse import urlparse
from ZeMusic import app
from pyrogram import Client, filters
from pyrogram.types import Message

@app.on_message(filters.command(["انستا"], ["."]))
async def download_instagram(c: app, m: Message):
    try:
        reel_ = m.command[1]
    except IndexError:
        await m.reply_text("≭︰إرسل رابط المقطع في الانستا .")
        return
    if not reel_.startswith("https://www.instagram.com/reel/"):
        await m.reply_text("≭︰عذراً ~ الرابط غير صالح .")
        return
    OwO = reel_.split(".",1)
    Reel_ = ".dd".join(OwO)
    try:
        await m.reply_video(Reel_)
        return
    except Exception:
        try:
            await m.reply_photo(Reel_)
            return
        except Exception:
            try:
                await m.reply_document(Reel_)
                return
            except Exception:
                await m.reply_text("Error")

@app.on_message(filters.command(["توك"], ["."]))
async def download_tiktok(c: app, m: Message):
    try:
        tiktok_ = m.command[1]
    except IndexError:
        await m.reply_text("≭︰إرسل رابط المقطع في التيك توك .")
        return
    if not tiktok_.startswith("https://vt.tiktok.com/"):
        await m.reply_text("≭︰عذراً ~ الرابط غير صالح .")
        return
    tiktok = tiktok_.split(".",1)
    tiktok_ = ".dd".join(tiktok)
    try:
        await m.reply_video(tiktok_)
        return
    except Exception:
        try:
            await m.reply_photo(tiktok_)
            return
        except Exception:
            try:
                await m.reply_document(tiktok_)
                return
            except Exception:
                await m.reply_text("Error")

@app.on_message(filters.command(["يوتيوب"], ["."]))
async def download_youtube(c: app, m: Message):
    try:
        youtube_ = m.command[1]
    except IndexError:
        await m.reply_text("≭︰إرسل رابط المقطع في اليوتيوب .")
        return
    if not youtube_.startswith("https://youtu.be/"):
        await m.reply_text("≭︰عذراً ~ الرابط غير صالح .")
        return
    youtube = youtube_.split(".",1)
    youtube_ = ".dd".join(youtube)
    try:
        await m.reply_video(youtube_)
        return
    except Exception:
        try:
            await m.reply_photo(youtube_)
            return
        except Exception:
            try:
                await m.reply_document(youtube_)
                return
            except Exception:
                await m.reply_text("Error")
