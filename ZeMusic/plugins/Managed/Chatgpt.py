import openai
from pyrogram import Client, filters
from ZeMusic import app

# إعداد مفتاح OpenAI API
openai.api_key = "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"  # استبدل بـ API Key الخاص بك

@app.on_message(filters.command(["رون"], ""))
def fetch_from_openai(client, message):
    # استخراج السؤال من الرسالة بعد "رون"
    query = " ".join(message.command[1:])
    
    if not query:
        message.reply("يرجى إضافة سؤال بعد أمر **رون**.")
        return

    try:
        # إرسال السؤال إلى OpenAI API للحصول على إجابة باستخدام الواجهة الجديدة
        response = openai.completions.create(
            model="gpt-3.5-turbo",  # أو gpt-4 إذا كان لديك حق الوصول
            prompt=query,
            max_tokens=150,  # يمكنك تعديل هذا حسب طول الإجابة
            temperature=0.7,  # تحكم في إبداع الإجابة
        )

        # استخراج الإجابة من الاستجابة
        answer = response['choices'][0]['text'].strip()

        if answer:
            message.reply_text(f"الإجابة: {answer}")
        else:
            message.reply_text("لم أتمكن من إيجاد إجابة للسؤال.")
    
    except Exception as e:
        message.reply_text(f"حدث خطأ: {str(e)}")
