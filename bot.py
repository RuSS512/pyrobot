from pyrogram import Client
from pyrogram.api.functions.channels import GetAdminLog
from pyrogram.api.types import (
    ChannelAdminLogEventActionDeleteMessage,
)
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

API_ID = int(os.getenv("API_ID"))  # Ваш API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # Ваш API Hash из my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ваш токен бота (если используется)

# Инициализация клиента
client = Client(
    "client",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN  # Уберите этот параметр, если работаете как userbot
)

# Функция для получения логов
def get_deleted_messages(channel_id):
    try:
        # Запрос логов администраторов
        result = client.send(
            GetAdminLog(
                channel=client.resolve_peer(channel_id),
                q="",
                max_id=0,
                min_id=0,
                limit=1000
            )
        )
        # Обработка логов
        for event in result.events:
            if isinstance(event.action, ChannelAdminLogEventActionDeleteMessage):
                deleted_message = event.action.message
                if deleted_message and deleted_message.message:
                    print(f"Удаленное сообщение: {deleted_message.message}")
                else:
                    print("Удаленное сообщение было пустым или не найдено.")
    except Exception as e:
        print(f"Ошибка при получении логов: {e}")


# Основная функция
def main():
    with client:
        print("Бот запущен и готов к работе!")
        channel = input("Введите ID или username канала: ")
        get_deleted_messages(channel)


if __name__ == "__main__":
    main()
