from pyrogram import Client
from pyrogram.raw.functions.channels import GetAdminLog
from pyrogram.raw.types import ChannelAdminLogEventActionDeleteMessage
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

API_ID = int(os.getenv("API_ID"))  # Ваш API ID
API_HASH = os.getenv("API_HASH")  # Ваш API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ваш токен бота
channel = os.getenv("CHANNEL_ID")  # Получаем ID или username канала

if not channel:
    raise ValueError("Переменная окружения CHANNEL_ID не задана!")

# Инициализация клиента
client = Client(
    "client",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Функция для получения удалённых сообщений
def get_deleted_messages(client, channel_id):
    try:
        result = client.invoke(
            GetAdminLog(
                channel=client.resolve_peer(channel_id),
                q="",
                max_id=0,
                min_id=0,
                limit=1000
            )
        )
        for event in result.events:
            if isinstance(event.action, ChannelAdminLogEventActionDeleteMessage):
                deleted_message = event.action.message
                if deleted_message and deleted_message.message:
                    print(f"Удалённое сообщение: {deleted_message.message}")
                else:
                    print("Удалённое сообщение было пустым или не найдено.")
    except Exception as e:
        print(f"Ошибка: {e}")

# Основной запуск
if __name__ == "__main__":
    print("Бот запущен!")
    client.start()  # Явно подключаем клиента
    get_deleted_messages(client, channel)
    client.stop()  # Явно отключаем клиента
