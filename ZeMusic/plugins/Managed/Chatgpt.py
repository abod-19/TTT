import os
import base64
import mimetypes
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from lexica import AsyncClient, languageModels, Messages
from ZeMusic import app


def get_prompt(message: Message) -> str | None:
    return message.text

def extract_content(response) -> str | None:
    content = response.get('content')
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return '\n'.join(item['text'] for item in content if isinstance(item, dict) and 'text' in item)
    elif isinstance(content, dict):
        if 'parts' in content and isinstance(content['parts'], list):
            return '\n'.join(part.get('text', '') for part in content['parts'] if 'text' in part)
        return content.get('text')
    return None


def format_response(model_name: str, content: str) -> str:
    return f"{content}"


async def handle_text_model(message: Message, model, model_name: str, as_messages=False):
    prompt = get_prompt(message)

    await message._client.send_chat_action(message.chat.id, ChatAction.TYPING)

    lexica_client = AsyncClient()
    try:
        data = [Messages(content=prompt, role="user")] if as_messages else prompt
        response = await lexica_client.ChatCompletion(data, model)
        content = extract_content(response)
        await message.reply_text(format_response(model_name, content) if content else "No content received from the API.", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
    finally:
        await lexica_client.close()


@app.on_message(filters.private)
async def gpt_handler(client: Client, message: Message):
    await handle_text_model(message, languageModels.gpt, "GPT", as_messages=True)
