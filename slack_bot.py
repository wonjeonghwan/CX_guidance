import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from DB import init_db, save_message
from rag_logic import generate_response
from datetime import datetime, timedelta
import threading
import time
from DB import get_messages_by_customer, get_last_message_by_customer, update_analysis_result
from analysis_llm import analyze_conversation
from google_sheet import export_conversations_to_sheet


customer_last_seen = {}

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
            
            customer_last_seen[customer_id] = datetime.now()
            
            # RAG 응답
            response = generate_response(message_body, message_id, customer_id)

            #Slack 출력
            say(channel=channel, text=f"📥 고객 `{customer_id}` 메시지 인식 완료!\n```{message_body}```")
            say(channel=channel, text=f"🤖 봇 응답: {response}")

        except Exception as e:
            print(f"❌ 처리 오류: {e}")
            say(channel=channel, text="⚠️ 고객 ID와 메시지 형식을 다시 확인해주세요.")
            
    elif text.startswith("@상담종료"):
        try:
            # customer_id 파싱
            customer_id = text.split("customer_id:")[-1].strip()
            print(f"🛑 상담 종료 요청 수신 → {customer_id}")

            # 메시지 불러오기
            messages = get_messages_by_customer(customer_id)
            level, issue = analyze_conversation(messages)
            last_msg = get_last_message_by_customer(customer_id)

            if last_msg:
                update_analysis_result(last_msg[0], level, issue)
                say(channel=channel, text=f"✅ `{customer_id}` 상담 종료 요약 완료\n• Level: `{level}`\n• Issue: `{issue}`")
            else:
                say(channel=channel, text=f"⚠️ `{customer_id}`의 대화 기록이 없습니다.")

        except Exception as e:
            print(f"❌ 상담종료 처리 실패: {e}")
            say(channel=channel, text=f"⚠️ 상담 종료 처리 중 오류가 발생했습니다.")
        
    else:
        say(channel=channel, text="⚠️ 고객 ID가 누락되었습니다. `@customer_id:` 형식으로 시작해주세요.")

def monitor_inactivate_customers():
    while True:
        time.sleep(60)
        now = datetime.now()
        for customer_id, last_time in list(customer_last_seen.items()):
            if now - last_time > timedelta(minutes=30):
                print(f"{customer_id} 30분 이상 활동 없음 → LLM 분석 시작")

                try:
                    messages = get_messages_by_customer(customer_id)
                    level, issue = analyze_conversation(messages)
                    last_msg = get_last_message_by_customer(customer_id)
                    if last_msg:
                        update_analysis_result(last_msg[0], level, issue)
                        print(f"✅ 저장 완료 → Level: {level}, issue: {issue}")
                except Exception as e:
                    print(f"❌ LLM 분석 실패: {e}")

def schedule_google_sheet_sync():
    while True:
        try:
            export_conversations_to_sheet()
            print("✅ Google 시트 동기화 완료")
        except Exception as e:
            print(f"❌ Google 시트 동기화 실패: {e}")
        time.sleep(60)

    
# 실행
if __name__ == "__main__":
    print("✅ Slack CX Bot 실행 중...")
    init_db()
    threading.Thread(target=monitor_inactivate_customers, daemon=True).start()
    threading.Thread(target=schedule_google_sheet_sync, daemon=True).start()
    SocketModeHandler(app, SLACK_APP_TOKEN).start()