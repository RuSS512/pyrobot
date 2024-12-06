from pyrogram import Client, filters
import sqlite3
import os

# Переменные окружения
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
client = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Настройка базы данных
conn = sqlite3.connect("messages.db")  # Создаётся локальная база данных messages.db
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,  -- Уникальный идентификатор сообщения
    chat_id INTEGER,                 -- Идентификатор группы/канала
    user_id INTEGER,                 -- Идентификатор отправителя
    text TEXT                        -- Текст сообщения
)
""")
conn.commit()

# Сохранение входящих сообщений в базу данных
@client.on_message(filters.group & ~filters.service)
def save_message(client, message):
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO messages (message_id, chat_id, user_id, text) 
        VALUES (?, ?, ?, ?)
        """, (
            message.id,  # Исправлено
            message.chat.id,
            message.from_user.id if message.from_user else None,
            message.text or ""
        ))
        conn.commit()
        print(f"Сохранено сообщение: {message.text}")
    except Exception as e:
        print(f"Ошибка при сохранении сообщения: {e}")

# Обработка удаления сообщений
@client.on_deleted_messages(filters.group)
def handle_deleted_messages(client, messages):
    for message in messages:
        try:
            cursor.execute("SELECT text FROM messages WHERE message_id = ?", (message.id,))  # Исправлено
            row = cursor.fetchone()
            if row:
                print(f"Удалено сообщение: {row[0]}")  # Логируем удалённое сообщение
            cursor.execute("DELETE FROM messages WHERE message_id = ?", (message.id,))  # Исправлено
            conn.commit()
        except Exception as e:
            print(f"Ошибка при обработке удаления сообщения: {e}")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен и готов к работе!")
    client.run()
