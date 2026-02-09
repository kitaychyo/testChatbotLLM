import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# OpenRouter client (OpenAI-compatible)
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# In-memory dialog storage
user_context = {}

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Новый запрос")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: Message):
    user_context[message.from_user.id] = []
    await message.answer(
        "Привет! Я бот с поддержкой ChatGPT через OpenRouter.\nКонтекст диалога сброшен.",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Отправь мне любой текст — я отвечу с помощью ChatGPT (OpenRouter).\n"
        "Команда /start или кнопка 'Новый запрос' сбрасывают контекст."
    )

@dp.message(F.text == "Новый запрос")
async def new_request(message: Message):
    user_context[message.from_user.id] = []
    await message.answer("Контекст диалога очищен. Можешь задать новый вопрос ✨")

@dp.message(F.text)
async def chatgpt_handler(message: Message):
    user_id = message.from_user.id

    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append({"role": "user", "content": message.text})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=user_context[user_id]
        )

        answer = response.choices[0].message.content
        user_context[user_id].append({"role": "assistant", "content": answer})

        await message.answer(answer)

    except Exception as e:
        await message.answer("Ошибка при обращении к OpenRouter API")
        logging.error(e)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())