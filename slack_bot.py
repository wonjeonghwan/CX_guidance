import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from DB import init_db, save_message, update_response
from rag_logic import generate_response

# 환경변수 로딩
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SOCKET_TOKEN")

# Slack 앱 초기화
app = App(token=SLACK_BOT_TOKEN)

# 메시지 이벤트 처리: 상담사가 복붙한 고객 메시지 감지
@app.event("message")
def handle_message_events(body, say):
    event = body.get("event", {})
    user = event.get("user")
    text = event.get("text")
    channel = event.get("channel")

    print(f"[수신] From {user}: {text}")

    # 봇 메시지 무시
    if 'bot_id' in event:
        return
    
    # 고객 ID가 포함된 메시지인 경우
    if text.startswith("@customer_id"):
        try:
            lines = text.split('\n', 1)
            customer_id = lines[0].replace("@customer_id:", "").strip()
            message_body = lines[1].strip()

            # DB저장
            message_id = save_message(customer_id, user, channel, message_body)
            
            # RAG 응답
            response = generate_response(message_body, message_id, customer_id)

            #Slack 출력
            say(channel=channel, text=f"📥 고객 `{customer_id}` 메시지 인식 완료!\n```{message_body}```")
            say(channel=channel, text=f"🤖 봇 응답: {response}")

        except Exception as e:
            print(f"❌ 처리 오류: {e}")
            say(channel=channel, text="⚠️ 고객 ID와 메시지 형식을 다시 확인해주세요.")
    else:
        say(channel=channel, text="⚠️ 고객 ID가 누락되었습니다. `@customer_id:` 형식으로 시작해주세요.")
# 실행
if __name__ == "__main__":
    print("✅ Slack CX Bot 실행 중...")
    init_db()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()