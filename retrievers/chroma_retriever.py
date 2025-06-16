from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

def get_chroma_retriever(persist_path: str = "persist", top_k: int = 4):
    embedding_model = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=persist_path, embedding_function=embedding_model)
    return vectordb.as_retriever(search_kwargs={"k": top_k})
