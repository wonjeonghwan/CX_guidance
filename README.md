# CX Manager Assistant

**Slack 기반 챗봇**으로, CS 매니저가 Slack에 고객 메시지를 붙여넣으면 내부 지식(Chroma)을 기반으로 LLM을 통해 **응답 생성**,
상담 종료 시에는 **Issue 요약 & 우선순위(Level) 분류**를 Google Sheet에 저장합니다.

## Features
- **Slack 연동**: `@customer_id:`로 시작하는 메시지를 감지해 DB 저장 → RAG 응답 → 채널에 바로 출력  
- **RAG 응답 생성**: 내부 문서를 ChromaDB에 벡터화하여 저장, 관련 맥락 검색 후 답변 생성  
- **대화 저장/조회**: SQLite에 고객별 대화(질문/답변/타임스탬프) 저장  
- **이슈 자동 분석**: `@상담종료 customer_id:...` 또는 30분 비활성 시 자동 분석( Issue / Level )  
- **리포트 자동화**: Google Sheet에 (상담일시, 고객ID, 우선순위, 이슈) 동기화


## ⚙️ Requirements

- Python 3.10+
- Packages
  - `langchain`, `langchain-openai`, `langchain-community`
  - `chromadb`
  - `openai` (LangChain OpenAI Embeddings/LLM 구동용)
  - `slack-bolt`, `slack-sdk`
  - `python-dotenv`
  - `gspread`, `oauth2client`
  - `sqlite3`

<img width="695" height="549" alt="image" src="https://github.com/user-attachments/assets/1a8dc098-5f48-40da-989e-119de6484d56" />
<img width="820" height="253" alt="image" src="https://github.com/user-attachments/assets/113e7cf7-08ad-45c0-9140-279b675a038c" />
