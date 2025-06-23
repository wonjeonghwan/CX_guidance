# export_to_google_sheet.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

def export_conversations_to_sheet():
    # 1. 인증
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CRED_PATH"), scope)
    client = gspread.authorize(creds)

    # 2. 시트 연결
    sheet = client.open("CX_요약_리포트").worksheet("요약")

    # 3. DB 연결
    conn = sqlite3.connect("chatbot.db")
    c = conn.cursor()
    c.execute("SELECT timestamp, customer_id, level, keyword, FROM conversations WHERE level IS NOT NULL ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    # 4. 시트 초기화 + 헤더
    sheet.clear()
    sheet.append_row(["상담일시", "고객 ID", "우선순위", "이슈 요약"])

    # 5. 시트에 행 추가
    for row in rows:
        sheet.append_row(row)
