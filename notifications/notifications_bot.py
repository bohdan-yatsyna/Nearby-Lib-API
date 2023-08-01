import os
import telebot

from dotenv import load_dotenv
from typing import Any

from borrowings.models import Borrowing
from users.models import User

load_dotenv()


def send_message(message: str) -> Any:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telebot.TeleBot(token=token)
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    return bot.send_message(chat_id, message)


def send_borrowing_create_notification(
        user: User,
        borrowing: Borrowing
) -> None:
    """
    Sends a message via Telegram bot to admin user
    about creating a new borrowing
    """

    message = (
        f"New borrowing is created by user:"
        f"{user.full_name}. \n"
        f"Book: {borrowing.book.title}, "
        f"with expected return date: {borrowing.expected_return_date}."
    )
    send_message(message)
