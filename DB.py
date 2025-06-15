import sqlite3
from datetime import datetime

# ✅ DB 초기화 (PK 이름은 number)
def init_db():
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        number INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        user_id TEXT,
        channel_id TEXT,
        message TEXT,
        response TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

# ✅ 메시지 저장
def save_message(customer_id, user_id, channel_id, message):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute('''INSERT INTO conversations (
        customer_id, user_id, channel_id, message, response, timestamp
    ) VALUES (?, ?, ?, ?, ?, ?)''',
    (customer_id, user_id, channel_id, message, None, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ✅ LLM 응답 저장
def update_response(number, response_text):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("UPDATE conversations SET response = ? WHERE number = ?", (response_text, number))
    conn.commit()
    conn.close()

# ✅ 특정 고객의 대화 이력 조회 (optional)
def get_messages_by_customer(customer_id):
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("SELECT number, message, response FROM conversations WHERE customer_id = ?", (customer_id,))
    rows = c.fetchall()
    conn.close()
    return rows