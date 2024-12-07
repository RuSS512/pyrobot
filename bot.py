from pyrogram import Client, filters
import sqlite3
import os
import threading
import time

# Переменные окружения
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Настройка базы данных
conn = sqlite3.connect("messages.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    user_id INTEGER,
    text TEXT
)
""")
conn.commit()

thread_local = threading.local()

def get_db_connection():
    if not hasattr(thread_local, "db"):
        thread_local.db = sqlite3.connect("messages.db", check_same_thread=False)
    return thread_local.db

# Сохранение сообщений
@client.on_message(filters.group & ~filters.service)
def save_message(client, message):
    try:
        text = message.text or "[Без текста]"
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO messages (message_id, chat_id, user_id, text)
        VALUES (?, ?, ?, ?)
        """, (
            message.id,
            message.chat.id,
            message.from_user.id if message.from_user else None,
            text
        ))
        db.commit()
        print(f"Сохранено сообщение: {text}")
    except Exception as e:
        print(f"Ошибка при сохранении сообщения: {e}")

# Проверка существования сообщений
def check_for_deleted_messages():
    while True:
        time.sleep(30)  # Проверка каждые 30 секунд
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT message_id, chat_id, text FROM messages")
        all_messages = cursor.fetchall()
        for message_id, chat_id, text in all_messages:
            try:
                # Проверяем существование сообщения
                message = client.get_messages(chat_id, message_ids=message_id)
                if not message or message.empty:  # Проверяем, вернулся ли пустой объект
                    print(f"Сообщение удалено: {text}")
                    cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
                    db.commit()
            except Exception as e:
                print(f"Ошибка при проверке сообщения {message_id}: {e}")
                cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
                db.commit()

if __name__ == "__main__":
    print("Бот запущен!")
    threading.Thread(target=check_for_deleted_messages, daemon=True).start()
    client.run()
