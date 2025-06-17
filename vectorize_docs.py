import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 경로 설정
docs_path = "./docs"
chroma_path = "./persist"

# 기존 벡터 DB 제거 (중복 저장 방지)
if os.path.exists(chroma_path):
    shutil.rmtree(chroma_path)

# 문서 로딩 및 메타데이터 추정
documents = []
for root, dirs, files in os.walk(docs_path):
    for fname in files:
        if not fname.endswith(".txt"):
            continue

        path = os.path.join(root, fname)
        loader = TextLoader(path, encoding="utf-8")
        raw_docs = loader.load()

        # 상대 경로 기준으로 category / subcategory 분류
        rel_path = os.path.relpath(path, docs_path)
        parts = rel_path.split(os.sep)
        category = parts[0] if len(parts) > 1 else "기타"
        subcategory = parts[1] if len(parts) > 2 else fname.replace(".txt", "")

        for doc in raw_docs:
            doc.metadata.update({
                "source_file": fname,
                "category": category,
                "subcategory": subcategory
            })
        documents.extend(raw_docs)

# 텍스트 청크 분할
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = splitter.split_documents(documents)

# 벡터화 + 저장
embedding = OpenAIEmbeddings()
chroma_db = Chroma.from_documents(splits, embedding, persist_directory=chroma_path)

print(f"✅ 벡터화 완료! 총 문서 수: {len(documents)} / 총 청크 수: {len(splits)}")
