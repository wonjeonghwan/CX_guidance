# rag_logic.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableMap, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Chroma Vector DB 로드
chroma_path = "persist"
embedding_model = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=chroma_path, embedding_function=embedding_model)
retriever = vectordb.as_retriever(search_kwargs={"k": 4})

# 2. 프롬프트 템플릿 정의
template = """
당신은 상담사가 환불 방어를 목적으로 다른 서비스를 제안할 수 있도록, 고객 불편을 빠르게 파악하고 상담사에게 다른 서비스나 등으로 우회하거나 해결방안을 제안 합니다.

고객 문의:
{question}

관련 내부 자료:
{context}

답변 원칙:
- 상담사를 위해 내부 자료를 기반으로 환불 방어 아이디어를 답변합니다.
- 고객의 상황을 파악하고 환불이 아닌 대체 서비스, 혜택으로 고객의 문제를 해결할 수 있는 방안을 반드시 구체적인 서비스와 함께 제시합니다.
- 불필요한 내용(인사, 문의 내용 확인)을 답변하지 않습니다.
- 문의 내용이 내부 자료와 관련 없는 경우 "서비스와 관련 없음" 출력

답변:
"""
prompt = PromptTemplate.from_template(template)

# 3. LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

# 4. 파이프라인 구성
chain = (
    {"context": retriever, "question": RunnableLambda(lambda x: x)}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. 예시 실행용 함수
def generate_response(user_question: str):
    return chain.invoke(user_question)

if __name__ == "__main__":
    print("=== RAG 봇 테스트 ===")
    q1 = "아이가 흥미를 느끼지 못해요, 아이에게 맞는 학습 방식이 아니에요. 학습할 시간이 없어요"
    q2 = "아이가 너무 어려워해서 이용 못해요. 환불 가능한가요?"
    q3 = "라이브클래스는 잘 하는데 GV레슨이나 숙제를 잘 영 안하려고 하네요...지금 환불하게 되면 비용 처리가 어떻게 될까요?"
    q4 = "사랑은 뭘까요?"
    for q in [q1, q2, q3, q4]:
        print(f"\n🙋 사용자: {q}")
        print("🤖 봇 응답:", generate_response(q))