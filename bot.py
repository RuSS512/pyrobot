from pyrogram import Client, filters
import sqlite3
import os
import threading
import time

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

def check_for_deleted_messages():
    while True:
        time.sleep(30)  # Проверка каждые 30 секунд
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT message_id, text FROM messages")
        all_messages = cursor.fetchall()
        for message_id, text in all_messages:
            try:
                # Проверяем, существует ли сообщение в Telegram
                client.get_messages(chat_id, message_ids=message_id)
            except:
                print(f"Сообщение удалено: {text}")
                cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
                db.commit()

if __name__ == "__main__":
    print("Бот запущен!")
    threading.Thread(target=check_for_deleted_messages, daemon=True).start()
    client.run()
