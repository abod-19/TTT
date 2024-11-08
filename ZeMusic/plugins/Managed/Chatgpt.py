import requests
from pyrogram import Client, filters
from ZeMusic import app


@app.on_message(filters.command(["رون"], ""))
def fetch_from_gemini(client, message):
    # استخراج السؤال من الرسالة بعد "رون"
    query = " ".join(message.command[1:])
    
    if not query:
        message.reply("يرجى إضافة سؤال بعد أمر **رون**.")
        return

    try:
        # إرسال طلب إلى API جيميني للحصول على البيانات
        response = requests.get(f"https://api.gemini.com/v1/pubticker/{query}")
        if response.status_code == 200:
            data = response.json()
            # عرض البيانات المسترجعة من API
            message.reply_text(f"الإجابة: {data['last']}")  # أو تخصيص الجزء الذي تريد عرضه من البيانات
        else:
            error_message = response.text
            message.reply_text(f"حدث خطأ أثناء جلب البيانات. الكود: {response.status_code}، التفاصيل: {error_message}")

    except Exception as e:
        message.reply_text(f"حدث خطأ: {str(e)}")
