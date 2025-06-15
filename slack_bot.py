import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from DB import init_db, save_message


# 환경변수 로딩
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SOCKET_TOKEN")

# Slack 앱 초기화
app = App(token=SLACK_BOT_TOKEN)

# 메시지 이벤트 처리: 상담사가 복붙한 고객 메시지 감지
@app.event("message")
def handle_message_events(body, say):
    user = body['event']['user']
    text = body['event']['text']
    channel = body['event']['channel']

    print(f"[수신] From {user}: {text}")

    # 봇 메시지 무시
    if 'bot_id' in body['event']:
        return
    
    if text.startswith("@customer_id"):
        try:
            lines = text.split('\n', 1)
            customer_id = lines[0].replace("@customer_id:", "").strip()
            message_body = lines[1].strip()

            save_message(customer_id, user, channel, message_body)

            say(channel=channel, text=f"📥 고객 `{customer_id}` 메시지 인식 완료!\n```{message_body}```")
        except Exception as e:
            say(channel=channel, text="⚠️ 고객 ID와 메시지 형식을 다시 확인해주세요.")
    else:
        say(channel=channel, text="⚠️ 고객 ID가 누락되었습니다. `@customer_id:` 형식으로 시작해주세요.")

    save_message(user, channel, text)
    say(channel=channel, text=f"📥 고객 메시지 인식: ```{text}```")


# 실행
if __name__ == "__main__":
    print("✅ Slack CX Bot 실행 중...")

    init_db()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
