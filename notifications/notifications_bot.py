import os
import telebot

from dotenv import load_dotenv
from typing import Any

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(token=token)
chat_id = os.getenv("BOT_CHAT_ID")


def send_message(message: str) -> Any:
    return bot.send_message(chat_id, message)
