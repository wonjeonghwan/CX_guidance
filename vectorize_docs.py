import os
import shutil
from langchain_community.document_loaders import TextLoader         # 문서 불러오기
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 텍스트 쪼개기
from langchain.embeddings import OpenAIEmbeddings                   # 문장 임베딩
from langchain_community.vectorstores import Chroma                 # 벡터DB

# 경로 설정
docs_path = "./docs"
chroma_path = "./persist"

# 기존 DB 제거 (중복 방지용)
if os.path.exists(chroma_path):
    shutil.rmtree(chroma_path)

# 문서 로딩
documents = []
for fname in os.listdir(docs_path):
    if fname.endswith(".txt"):
        path = os.path.join(docs_path, fname)
        loader = TextLoader(path, encoding="utf-8")
        raw_docs = loader.load()

        # 메타데이터 추정
        if "커리큘럼" in fname:
            category, sub = "서비스소개", "커리큘럼"
        elif "약관" in fname:
            category, sub = "약관", "서비스 이용"
        elif "결제" in fname:
            category, sub = "FAQ", "결제"
        elif "환불" in fname:
            category, sub = "FAQ", "환불"
        elif "배송" in fname:
            category, sub = "FAQ", "배송"
        else:
            category, sub = "기타", "기타"

        for doc in raw_docs:
            doc.metadata.update({
                "source_file": fname,
                "category": category,
                "subcategory": sub
            })
        documents.extend(raw_docs)

# 분할
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
splits = splitter.split_documents(documents)

# 임베딩 + Chroma 저장
embedding = OpenAIEmbeddings()
chroma_db = Chroma.from_documents(splits, embedding, persist_directory=chroma_path)

print(f"✅ 벡터화 완료! 총 문서 수: {len(documents)} / 총 청크 수: {len(splits)}")
