import openai
from pyrogram import Client, filters
from ZeMusic import app

# إعداد مفتاح OpenAI API
openai.api_key = "YOUR_OPENAI_API_KEY"  # استبدل بـ API Key الخاص بك

@app.on_message(filters.command(["رون"], ""))
def fetch_from_openai(client, message):
    # استخراج السؤال من الرسالة بعد "رون"
    query = " ".join(message.command[1:])
    
    if not query:
        message.reply("يرجى إضافة سؤال بعد أمر **رون**.")
        return

    try:
        # إرسال السؤال إلى OpenAI API للحصول على إجابة
        response = openai.chat_completions.create(
            model="gpt-4",  # أو يمكنك استخدام gpt-3.5 حسب الحاجة
            messages=[{"role": "user", "content": query}],
        )

        # استخراج الإجابة من الاستجابة
        answer = response['choices'][0]['message']['content'].strip()

        if answer:
            message.reply_text(f"الإجابة: {answer}")
        else:
            message.reply_text("لم أتمكن من إيجاد إجابة للسؤال.")
    
    except Exception as e:
        message.reply_text(f"حدث خطأ: {str(e)}")
