from os import path
from ZeMusic.utils.formatters import seconds_to_min
import requests

class SoundAPI:
    def __init__(self):
        self.base_url = "https://api.soundcloud.com"
        self.client_id = "b277e5a6-7a42-4b09-b0bf-6d61daa0fd92"  # تأكد من إضافة client_id الخاص بك من SoundCloud
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
        }

    async def valid(self, link: str):
        if "soundcloud.com" in link:
            return True
        else:
            return False

    async def download(self, url):
        # تحميل المقطع من SoundCloud
        track_id = self.get_track_id(url)
        if not track_id:
            return False
        
        track_info = self.get_track_info(track_id)
        if not track_info:
            return False

        track_url = track_info['stream_url'] + "?client_id=" + self.client_id
        duration_min = seconds_to_min(track_info['duration'] / 1000)  # تحويل المدة من ميلي ثانية إلى دقائق
        
        # حفظ البيانات حول المسار
        track_details = {
            "title": track_info["title"],
            "duration_sec": track_info["duration"] / 1000,  # تحويل المدة من ميلي ثانية إلى ثواني
            "duration_min": duration_min,
            "uploader": track_info["user"]["username"],
            "filepath": track_url,
        }
        return track_details, track_url

    async def search(self, query: str):
        """بحث عن الأغنية باستخدام النص المدخل في SoundCloud"""
        search_url = f"{self.base_url}/tracks?client_id={self.client_id}&q={query}"

        try:
            response = requests.get(search_url)
            tracks = response.json()
            if not tracks:
                return None
        except Exception as e:
            return None

        # استخراج أول نتيجة من البحث
        track = tracks[0]
        track_details = {
            "title": track['title'],
            "url": track['permalink_url'],
            "duration_sec": track['duration'] / 1000,  # تحويل المدة من ميلي ثانية إلى ثواني
            "uploader": track['user']['username'],
            "thumbnail": track.get('artwork_url', None),
        }
        return track_details

    def get_track_id(self, url):
        """استخراج track_id من الرابط"""
        if 'soundcloud.com' in url:
            return url.split("/")[-1]
        return None

    def get_track_info(self, track_id):
        """جلب معلومات الأغنية من SoundCloud"""
        track_info_url = f"{self.base_url}/tracks/{track_id}?client_id={self.client_id}"
        try:
            response = requests.get(track_info_url)
            return response.json()
        except:
            return None
