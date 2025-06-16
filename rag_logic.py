# rag_logic.py (메인 실행 파일)
from prompts.service_suggest_prompt import refund_prompt
from retrievers.chroma_retriever import get_chroma_retriever
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from DB import update_response, get_messages_by_customer

# 1. 모델 및 리트리버 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
retriever = get_chroma_retriever()

# 2. 체인 구성
chain = (
    {"context": retriever, "question": RunnableLambda(lambda x: x)}
    | refund_prompt
    | llm
    | StrOutputParser()
)

# 3. 실행용 함수
def generate_response(user_question: str, number: int, customer_id: str):
    # 1. 이전 대화 이력 조회
    past_logs = get_messages_by_customer(customer_id)
    history_context = "\n".join(
        f"Q: {msg}\nA: {res}" for _, msg, res in past_logs if res
    )

    # 2. 대화 이력 + 현재 질문을 묶어서 전달
    composite_question = f"{history_context}\n\n[현재 질문]\n{user_question}"

    # 3. RAG 실행 및 DB 저장
    response = chain.invoke(composite_question)
    update_response(number, response)
    return response

# 4. 테스트용 코드
if __name__ == "__main__":
    print("=== RAG 봇 테스트 ===")
    q1 = "아이가 흥미를 느끼지 못해요, 아이에게 맞는 학습 방식이 아니에요. 학습할 시간이 없어요"
    q2 = "아이가 너무 어려워해서 이용 못해요. 환불 가능한가요?"
    q3 = "라이브클래스는 잘 하는데 GV레슨이나 숙제를 잘 영 안하려고 하네요...지금 환불하게 되면 비용 처리가 어떻게 될까요?"
    q4 = "사랑은 뭘까요?"
    for q in [q1, q2, q3, q4]:
        print(f"\n🙋 사용자: {q}")
        print("🤖 봇 응답:", generate_response(q))
