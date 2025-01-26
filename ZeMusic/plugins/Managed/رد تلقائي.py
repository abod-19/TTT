from pyrogram import Client, filters
import config

# إعداد الجلسة
api_id = config.API_ID  # استبدل بـ API ID الخاص بك
api_hash = config.API_HASH  # استبدل بـ API Hash الخاص بك
session_name = str(config.STRING1)  # اسم الجلسة أو اتركه افتراضيًا

# إنشاء عميل Pyrogram
ap = Client(
  session_name,
  api_id=api_id,
  api_hash=api_hash,
  no_updates=True
)

# فلتر الرسائل الخاصة والرد التلقائي
@ap.on_message(filters.private & ~filters.me)  # يستثني رسائلك
def auto_reply(client, message):
    reply_text = "عندك اي مشكله قم بمراسله المطور @BBFYY"
    message.reply_text(reply_text)

# تشغيل البوت
if __name__ == "__main__":
    print("البوت يعمل... اضغط Ctrl+C للإيقاف")
    ap.run()
