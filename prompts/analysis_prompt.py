# prompts/analysis_prompt.py
from langchain_core.prompts import PromptTemplate

conversation_analysis_template = """
당신은 에듀테크 서비스의 고객지원 분석가.
다음은 고객과 AI 챗봇 간의 상담 대화를 분석하여 아래 정보를 추출하세요.

1. Issue : 문의의 핵심 이슈를 한 줄로 요약

[지침]
- 문장은 1줄로 요약
- 고객이 겪은 "불편"이나 "문의사항"이 명확하게 드러나야 함
- UX 감정이 아닌 기능·구조적 이슈 위주로 요약

[출력 예시]
라이브 수업 입장이 불가하여 학습 진행이 불가


2. Level : 시스템 크리티컬리티 관점에서 이슈 우선순위를 분류

[우선순위 기준]
- P0 (Blocker): 로그인, 결제, 개인정보 등 중단/위험 이슈
- P1 (Critical): 다수 사용자에게 영향 주는 핵심 기능 오류
- P2 (Major): 기능 불안정, UI 혼란, 일부 사용자 영향
- P3 (Minor): 사용은 가능하나 불편한 UX
- P4 (Nice-to-have): 개선 제안, 기능 요청

[출력 형식]
우선순위: P1

--- 대화 내용 ---
{conversation}
--- 끝 ---

응답 형식:
Level: <우선순위>
Issue: <이슈>
"""

conversation_analysis_prompt = PromptTemplate.from_template(conversation_analysis_template)
