# analysis_llm.py
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.analysis_prompt import conversation_analysis_prompt

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

chain = (
    conversation_analysis_prompt
    | llm
    | StrOutputParser()
)

def analyze_conversation(messages):
    """
    messages: [(number, message, response)] 형태
    returns: (level, keywords)
    """
    text = ""
    for number, message, response in messages:
        text += f"[고객] {message}\n"
        if response:
            text += f"[봇] {response}\n"

    result = chain.invoke({"conversation": text})
    print("🧠 LLM 분석 결과:\n", result)

    try:
        level_line = next(line for line in result.splitlines() if line.startswith("Level:"))
        issue_line = next(line for line in result.splitlines() if line.startswith("Issue:"))
        level = level_line.replace("Level:", "").strip()
        issue = issue_line.replace("Issue:", "").strip()
        return level, issue
    except Exception as e:
        print(f"❌ 파싱 실패: {e}")
        return "Unknown", "분석 실패"
